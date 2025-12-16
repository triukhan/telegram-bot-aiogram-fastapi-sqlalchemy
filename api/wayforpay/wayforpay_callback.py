from fastapi import APIRouter, Request

from api.wayforpay.utils import generate_ok, validate_signature, NEGATIVE_TEXTS_MAP, logger
from app import App
from contextlib import suppress
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

from db.models import User, Subscription
from texts import FIRST_FAILURE, SECOND_FAILURE, DECLINED, IN_PROGRESS, EXPIRED, UNEXPECTED_REQUEST

router = APIRouter(prefix='/wayforpay-callback')


@router.post('')
async def wayforpay_callback(request: Request):
    data = await request.json()
    app: App = request.app.state.app
    order_reference, status = validate_signature(data)
    subscription, user_id = await find_subscription_and_user_id(app, data)
    user: User = await app.get_or_create_user(user_id)
    logger.info(f'WFP -> {data}')

    if subscription:
        return await process_existing_subscription(app, user, subscription, order_reference, status, data.get('amount'))
    else:
        return await process_new_subscription(app, user, order_reference, status, data.get('regularMode'))


async def process_existing_subscription(
        app: App,
        user: User,
        subscription: Subscription,
        order_reference: str,
        status: str,
        amount: int
):
    user_id, last_payment_ts = user.id, subscription.last_payment_date

    if subscription.order_reference not in order_reference:
        logger.info(f'wrong order_ref <{order_reference}>. ignored. user: <{user_id}>')
        return generate_ok(order_reference)
    if status in {'Removed', 'Refunded', 'Suspended'}:
        await app.bot.save_send_message(
            user_id, NEGATIVE_TEXTS_MAP[status], reply_markup=await app.get_main_keyboard(user)
        )
        await app.kick_and_remove_from_db(user_id)
        return generate_ok(order_reference)

    months = 6 if amount == 60 else 1
    next_payment_ts = datetime.fromtimestamp(last_payment_ts) + relativedelta(months=months)

    if datetime.now() < next_payment_ts - timedelta(days=5) and not subscription.unsuccessful_payment:
        logger.info(f'user <{user_id}>: callback ignored, subscription is still valid until {next_payment_ts}')
        return generate_ok(order_reference)

    if status == 'Approved':
        updated_data = {
            'last_payment_date': int(datetime.now().timestamp()),
            'unsuccessful_payment': False,
            'last_reminder_sent': None
        }
        await app.db.subscriptions.update(user_id, updated_data)
        logger.info(f'updated payment for existing user <{user_id}>')
    elif status == 'Active':
        return generate_ok(order_reference)
    elif not subscription.unsuccessful_payment:
        await app.db.subscriptions.update(user_id, {'unsuccessful_payment': True})
        logger.info(f'first unsuccessful payment for user <{user_id}>. Status: {status}')
        await app.bot.save_send_message(user_id, FIRST_FAILURE)
    else:
        with suppress(Exception):
            await app.wayforpay.unsubscribe(subscription.order_reference)
        await app.bot.save_send_message(user_id, SECOND_FAILURE, reply_markup=await app.get_main_keyboard(user))
        await app.kick_and_remove_from_db(user_id)
        logger.info(f'user <{user_id}> was removed due to repeated failed payments. Status: {status}')
    return generate_ok(order_reference)


async def process_new_subscription(app: App, user: User, order_reference: str, status: str, regular_mode: str):
    if status == 'Approved':
        await app.process_success_payment(user.id, order_reference, regular_mode)
    else:
        await app.bot.save_send_message(user.id, {
            'Declined': DECLINED,
            'InProcessing': IN_PROGRESS + str(order_reference),
            'Pending': IN_PROGRESS + str(order_reference),
            'Expired': EXPIRED
        }.get(status, UNEXPECTED_REQUEST + str(order_reference)), reply_markup=await app.get_main_keyboard(user))
    return generate_ok(order_reference)


async def find_subscription_and_user_id(app: App, data: dict):
    order_reference = data.get('orderReference')
    subscription = await app.db.subscriptions.get_by_order(order_reference)
    if subscription:
        return subscription, subscription.user_id

    user_id = int(data.get('clientName'))
    return await app.db.subscriptions.get(user_id), user_id
