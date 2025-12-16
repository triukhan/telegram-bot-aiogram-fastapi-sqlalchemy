from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from telegram.utils import send_product_list
from texts import WRITE_PRODUCT_ID, MUST_BE_INT, WRITE_EDIT_FIELD, WRITE_NEW_VALUE, \
    EDIT_SUCCESS

edit_product_router = Router()


class ProductEdit(StatesGroup):
    id_state = State()
    field = State()
    value = State()


@edit_product_router.callback_query(lambda c: c.data == 'edit_product')
async def handle_edit_product(callback: CallbackQuery, state: FSMContext):
    app = callback.message.bot.state
    user = await app.db.users.get(callback.from_user.id)
    if not user.is_admin:
        return

    await send_product_list(await app.db.products.get_all(), callback)
    await callback.message.answer(WRITE_PRODUCT_ID)
    await state.set_state(ProductEdit.id_state)


@edit_product_router.message(ProductEdit.id_state)
async def process_edit_id(message: Message, state: FSMContext):
    try:
        product_id = int(message.text)
    except ValueError:
        await message.answer(MUST_BE_INT)
        return

    await state.update_data(id=product_id)
    await message.answer(WRITE_EDIT_FIELD)
    await state.set_state(ProductEdit.field)


@edit_product_router.message(ProductEdit.field)
async def process_edit_field(message: Message, state: FSMContext):
    await state.update_data(field=message.text.lower())
    await message.answer(WRITE_NEW_VALUE)
    await state.set_state(ProductEdit.value)


@edit_product_router.message(ProductEdit.value)
async def process_edit_value(message: Message, state: FSMContext):
    app = message.bot.state
    data = await state.get_data()
    product_id, field, value = data['id'], data['field'], message.text

    if field == 'price':
        value = int(value)

    await app.db.products.update(product_id, field, value)
    await message.answer(EDIT_SUCCESS.format(data['field'], value, product_id))
    await state.clear()
