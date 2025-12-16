
from button_texts import SUBSCRIPTION, ONE_MONTH, SIX_MONTH, CHECK_SUBSCRIPTION, UNSUBSCRIBE, MANAGE_SUBSCRIPTION, \
    BACK_TO_MAIN
from telegram.utils import private_only
from texts import CHOOSE_FREQ, UNSUB, SUB_ABSENT, PAYMENT_ERROR, BUY_SUBSCRIPTION, UNSUB_OR_CHECK_STATUS_MENU, \
    BUY_SUB_MENU
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, \
    KeyboardButton

from utils import logger

subscription_router = Router()


@subscription_router.message(F.text == SUBSCRIPTION)
@private_only
async def handle_buy(message: Message):
    tg_user, app = message.from_user, message.bot.state
    logger.log_user('buy access', tg_user)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=ONE_MONTH, callback_data='buy_1_month')],
        [InlineKeyboardButton(text=SIX_MONTH, callback_data='buy_6_months')]
    ])
    await message.answer(CHOOSE_FREQ, reply_markup=keyboard)


@subscription_router.callback_query(F.data.in_({'buy_1_month', 'buy_6_months'}))
async def process_buy_choice(callback: CallbackQuery):
    tg_user, app = callback.from_user, callback.message.bot.state
    six_months = callback.data == 'buy_6_months'
    logger.log_user('buy choice', tg_user)

    try:
        link = await app.generate_subscription_invoice(tg_user.id, six_month=six_months)
    except Exception:
        await callback.message.answer(PAYMENT_ERROR)
        return

    await callback.message.edit_text(BUY_SUBSCRIPTION.format(link))
    await callback.answer()


@subscription_router.message(F.text == CHECK_SUBSCRIPTION)
@private_only
async def handle_status_check(message: Message):
    tg_user, app = message.from_user, message.bot.state
    user = await app.get_or_create_user(tg_user.id)
    subscription = await app.db.subscriptions.get(user.id)
    logger.log_user('check sub', tg_user)

    if subscription:
        await app.check_status(user, subscription)
    else:
        await message.answer(SUB_ABSENT, reply_markup=await app.get_main_keyboard(user))


@subscription_router.message(F.text == UNSUBSCRIBE)
@private_only
async def handle_unsub(message: Message):
    tg_user, app = message.from_user, message.bot.state
    user = await app.db.users.get(tg_user.id)
    subscription = await app.db.subscriptions.get(user.id)
    logger.log_user('unsub', tg_user)

    if subscription:
        await app.wayforpay.unsubscribe(subscription.order_reference)
    await app.kick_and_remove_from_db(subscription.user_id)
    await message.answer(UNSUB, reply_markup=app.get_main_keyboard(user))


@subscription_router.message(F.text == MANAGE_SUBSCRIPTION)
@private_only
async def handle_subscription(message: Message):
    tg_user, app = message.from_user, message.bot.state
    subscription = await app.db.subscriptions.get(message.from_user.id)
    logger.log_user('handle sub', tg_user)

    text = UNSUB_OR_CHECK_STATUS_MENU if subscription else BUY_SUB_MENU
    keyboard = [
        [KeyboardButton(text=UNSUBSCRIBE if subscription else BUY_SUBSCRIPTION)],
        [KeyboardButton(text=CHECK_SUBSCRIPTION)],
        [KeyboardButton(text=BACK_TO_MAIN)],
    ]
    await message.answer(text, reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True))
