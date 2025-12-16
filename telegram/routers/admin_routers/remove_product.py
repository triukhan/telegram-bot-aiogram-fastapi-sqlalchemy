from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from telegram.utils import send_product_list
from texts import WRITE_PRODUCT_ID_REMOVE, MUST_BE_INT, PRODUCT_REMOVED

remove_product_router = Router()


class ProductRemove(StatesGroup):
    id_state = State()


@remove_product_router.callback_query(lambda c: c.data == 'remove_product')
async def handle_remove_product(callback: CallbackQuery, state: FSMContext):
    app = callback.message.bot.state

    await send_product_list(await app.db.products.get_all(), callback)
    await callback.message.answer(WRITE_PRODUCT_ID_REMOVE)
    await state.set_state(ProductRemove.id_state)


@remove_product_router.message(ProductRemove.id_state)
async def process_remove_product_id(message: Message, state: FSMContext):
    app = message.bot.state

    try:
        product_id = int(message.text)
    except ValueError:
        await message.answer(MUST_BE_INT)
        return

    await app.db.products.remove(product_id)
    await message.answer(PRODUCT_REMOVED.format(str(product_id)))
    await state.clear()
