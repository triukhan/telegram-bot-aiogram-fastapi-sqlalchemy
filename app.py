from datetime import datetime

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from dotenv import load_dotenv

from api.wayforpay.core import WayForPay
from db.app_db import AppDB
from db.models import User, Subscription
from telegram.bot import AppBot
from telegram.utils import ProductStatus
from texts import SUB_ABSENT, ACTIVE_SUBSCRIPTION, SUCCESS_PAYMENT, LINK_CHAT, LINK_CHANNEL, SUBSCRIPTION_NAME
from utils import logger, get_admin_keyboard

load_dotenv()


class App:
    def __init__(self, db: AppDB):
        self.bot = AppBot()
        self.db = db
        self.wayforpay = WayForPay()
        self.bot.state = self

    @classmethod
    async def create(cls):
        db = AppDB()
        await db.init_models()
        return cls(db)

    async def kick_and_remove_from_db(self, user_id: int):
        await self.bot.kick_from_chat_and_channel(user_id)
        await self.db.subscriptions.remove(user_id)

    async def check_status(self, user: User, subscription: Subscription):
        order_reference, user_id = subscription.order_reference, user.id
        response = await self.wayforpay.check_payment_status(order_reference)

        if response.get('status') == 'Active':
            last_paid_ts = response.get('lastPayedDate')
            if last_paid_ts:
                await self.db.subscriptions.update(user_id, {'last_payment_date': last_paid_ts})

            next_payment = datetime.fromtimestamp(response.get('nextPaymentDate')).date()
            formatted_date = next_payment.strftime('%-d-%B-%Y')

            await self.bot.save_send_message(user_id, ACTIVE_SUBSCRIPTION.format(formatted_date))
        else:
            await self.kick_and_remove_from_db(user_id)
            await self.bot.save_send_message(user_id, SUB_ABSENT, reply_markup=await self.get_main_keyboard(user))

    async def send_broadcast_message(self, text: str, product_id: int | str):
        if product_id == '-':
            users = await self.db.users.get_all()
            for user in users:
                await self.bot.save_send_message(user.id, text, reply_markup=await self.get_main_keyboard(user))
        else:
            for user_id in await self.db.get_user_ids_by_product_id(product_id):
                await self.bot.save_send_message(user_id, text)

    async def process_success_payment(self, user_id: int, order_reference: str, regular_mode: str):
        await self.db.subscriptions.add(user_id, order_reference, regular_mode)
        chat_link, channel_link = await self.bot.generate_invite_links()

        await self.bot.save_send_message(user_id, SUCCESS_PAYMENT)
        await self.bot.save_send_message(user_id, LINK_CHAT.format(chat_link))
        await self.bot.save_send_message(
            user_id,
            LINK_CHANNEL.format(channel_link),
            reply_markup=await self._get_keyboard(await self.db.users.get(user_id))
        )
        logger.info(f'{user_id} received success payment. invited to chat and channel')

    async def get_or_create_user(self, user_id: int):
        user = await self.db.users.get(user_id)
        if user is None:
            user = await self.db.users.add(user_id)
        return user

    async def generate_subscription_invoice(self, user_id, *, six_month) -> ReplyKeyboardMarkup:
        price, period = (90, 'halfyearly') if six_month else (15, 'monthly')
        return await self.wayforpay.generate_invoice(user_id, SUBSCRIPTION_NAME, price, period)

    async def _get_keyboard(self, user: User):
        actual_products = [product for product in await self.db.products.get_all() if product.status == ProductStatus.ACTIVE]
        if user:
            user_orders = [order for order in await self.db.orders.get_by_user(user.id)]
            is_subscribed = bool(await self.db.subscriptions.get(user.id))
        else:
            user_orders = []
            is_subscribed = False

        logger.info(f'keyboard[{user.id}] - orders: {user_orders} | subscribed: {is_subscribed}')
        return self.bot.get_keyboard_with_products(actual_products, user_orders, is_subscribed)

    async def get_main_keyboard(self, user: User) -> InlineKeyboardMarkup:
        if user and user.is_admin:
            return get_admin_keyboard()
        return await self._get_keyboard(user)

    async def get_school_keyboard_with_products(self):
        return self.bot.get_school_keyboard(await self.db.products.get_all())

    async def get_records_keyboard_with_products(self):
        return self.bot.get_records_keyboard(await self.db.products.get_all())

    async def generate_invoice_url(self, product_id: int, user_id: int):
        product = await self.db.products.get(product_id)
        return await self.wayforpay.generate_invoice(user_id, product.name, product.price)
