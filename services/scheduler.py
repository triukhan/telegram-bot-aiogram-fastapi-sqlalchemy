from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app import App
from db.models import Subscription
from texts import NOT_ACTIVE_KICK, PAYMENT_IN_3_DAYS
from utils import logger


KYIV = ZoneInfo('Europe/Kyiv')


async def notify_expiring_users_job(app: App):
    now = datetime.now(KYIV)
    subscriptions: list[Subscription] = await app.db.subscriptions.get_all()
    logger.info('--- Scheduler started ---')

    for subscription in subscriptions:
        user_id = subscription.user_id
        last_payment = datetime.fromtimestamp(subscription.last_payment_date, tz=KYIV)

        if subscription.payment_period == 'halfyearly':
            notify_date = last_payment + relativedelta(months=6) - timedelta(days=3)
        else:
            notify_date = last_payment + relativedelta(months=1) - timedelta(days=3)

        if subscription.last_reminder_sent is not None:
            last_reminder = datetime.fromtimestamp(subscription.last_reminder_sent, tz=KYIV)
            # if already sent
            if last_reminder >= notify_date:
                logger.info(f'skipped `{user_id}`. Already sent.')
                continue

        time_diff = (now - notify_date).total_seconds()  # if positive -> notify date is passed
        # until notify_date remain under 1 hour
        if time_diff > -3600:
            response = await app.wayforpay.check_payment_status(subscription.order_reference)
            if response.get('status') != 'Active':
                logger.error(f'user <{user_id}> is not active.')
                await app.bot.save_send_message(
                    user_id, NOT_ACTIVE_KICK, reply_markup=await app.get_main_keyboard(await app.db.users.get(user_id))
                )
                await app.bot.kick_and_remove_from_db(user_id)
                continue

            next_payment_date = datetime.fromtimestamp(response['nextPaymentDate'], tz=KYIV)
            if next_payment_date > now + timedelta(days=3):
                logger.info(f'user <{user_id}> skipped. next payment date: {str(next_payment_date)}')
                continue

            await app.bot.save_send_message(user_id, PAYMENT_IN_3_DAYS)
            logger.info(f'user <{user_id}> was notified n about payment in 3 days')
            await app.db.subscriptions.update(user_id, {'last_reminder_sent': int(now.timestamp())})

        logger.info(f'user <{user_id}> skipped')

    logger.info('--- scheduler finished ---')


def start_scheduler(app: App):
    scheduler = AsyncIOScheduler(timezone=KYIV)
    scheduler.add_job(
        notify_expiring_users_job,
        trigger=CronTrigger(hour=8, minute=0),
        args=[app],
        id='notify_expiring_users',
        replace_existing=True
    )
    scheduler.start()
