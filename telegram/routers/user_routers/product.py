from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from button_texts import MY_PRODUCTS, BUY
from telegram.utils import private_only
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from texts import PRODUCT_COST, ORDER_INFO, SHOW_INVOICE, ORDER_LIST
from utils import logger


user_product_router = Router()


async def get_keyboard_with_orders(app, user_id: int):
    rows = await app.db.get_orders_with_products(user_id)
    order_keyboard = [
        InlineKeyboardButton(text=product.name, callback_data=f'show_order_{order.wfp_order_reference}')
        for order, product in rows
    ]

    return InlineKeyboardMarkup(inline_keyboard=[order_keyboard])


async def is_product_click(message: Message) -> bool:
    app, chat_type = message.bot.state, message.chat.type
    product = await app.db.products.get_by_name(message.text)

    return product is not None


@user_product_router.message(F.text == MY_PRODUCTS)
@private_only
async def handle_click_my_products(message: Message):
    tg_user, app = message.from_user, message.bot.state
    logger.log_user(f'my products', tg_user)

    keyboard = await get_keyboard_with_orders(app, tg_user.id)
    await message.answer(ORDER_LIST, reply_markup=keyboard, parse_mode='Markdown')


@user_product_router.callback_query(lambda c: c.data.startswith('buy_'))
async def handle_buy_product(callback: CallbackQuery):
    tg_user, app, product_id = callback.from_user, callback.message.bot.state, int(callback.data.split('_')[1])
    logger.log_user(f'buy product <{product_id}>', tg_user)

    link = await app.generate_invoice_url(product_id, tg_user.id)
    await callback.message.answer(SHOW_INVOICE.format(link), parse_mode=None)


@user_product_router.callback_query(lambda c: c.data.startswith('show_order_'))
async def handle_show_order(callback: CallbackQuery):
    tg_user, app, order_ref = callback.from_user, callback.message.bot.state, callback.data.split('_')[-1]
    order = await app.db.orders.get(order_ref)
    product = await app.db.products.get(order.product_id)
    logger.log_user(f'show order <{order_ref}>', tg_user)

    await callback.message.answer(ORDER_INFO.format(product.name, product.description, product.link), parse_mode=None)


@user_product_router.message(is_product_click)
@private_only
async def process_buy_click(message: Message):
    tg_user, app = message.from_user, message.bot.state
    product = await app.db.products.get_by_name(message.text)
    await app.get_or_create_user(tg_user.id)
    logger.log_user(f'process buy <{message.text}>', tg_user)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=BUY, callback_data=f'buy_{product.id}')]]
    )

    await message.answer(PRODUCT_COST.format(product.name, product.description, product.price), reply_markup=keyboard)
