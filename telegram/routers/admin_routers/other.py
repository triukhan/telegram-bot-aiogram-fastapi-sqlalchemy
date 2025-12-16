from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from button_texts import ADMIN_ANSWER, ADMIN_PAUSE, ADMIN_CLOSE
from telegram.utils import MAX_MESSAGE_LENGTH
from texts import NEW_CHAT_RECEIVED, NO_CHATS, ALL_ORDERS, NO_ORDERS

admin_other_router = Router()


@admin_other_router.callback_query(lambda c: c.data == 'all_supports')
async def handle_all_supports(callback: CallbackQuery):
    tg_user, app = callback.from_user, callback.bot.state
    chats = await app.db.support_chats.get_all()

    if not chats:
        await callback.message.answer(NO_CHATS)
        return

    for chat in chats:
        kb = InlineKeyboardBuilder()
        kb.button(text=ADMIN_ANSWER, callback_data=f'support_reply:{chat.user_id}')
        kb.button(text=ADMIN_PAUSE, callback_data=f'support_pause:{chat.user_id}')
        kb.button(text=ADMIN_CLOSE, callback_data=f'support_close:{chat.user_id}')
        await callback.message.answer(NEW_CHAT_RECEIVED.format(chat.user_id), reply_markup=kb.as_markup())


@admin_other_router.callback_query(lambda c: c.data == 'all_orders')
async def handle_all_orders(callback: CallbackQuery):
    tg_user, app = callback.from_user, callback.bot.state
    orders = await app.db.orders.get_all()
    final_string = ''

    for order in orders:
        product = await app.db.products.get(order.product_id)
        date = order.purchased_at.strftime('%Y-%m-%d %H:%M')
        final_string += (ALL_ORDERS.format(order.user_id, product.name, date, order.wfp_order_reference))

    if not final_string:
        await callback.message.answer(NO_ORDERS)
        return

    for i in range(0, len(final_string), MAX_MESSAGE_LENGTH):
        chunk = final_string[i:i + MAX_MESSAGE_LENGTH]
        await callback.message.answer(chunk)
