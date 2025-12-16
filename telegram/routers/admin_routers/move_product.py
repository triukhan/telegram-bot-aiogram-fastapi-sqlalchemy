from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from telegram.utils import ProductStatus, send_product_list
from texts import WRITE_PRODUCT_ID, MUST_BE_INT, CHOOSE_CATEGORY, MUST_BE_CATEGORY, PRODUCT_MOVED

move_product_router = Router()

STATUS_MAP = {
    1: ProductStatus.ACTIVE,
    2: ProductStatus.RECORDS,
    3: ProductStatus.SCHOOL,
    4: ProductStatus.ARCHIVED,
}


class ProductMove(StatesGroup):
    id_state = State()
    choice_state = State()


@move_product_router.callback_query(lambda c: c.data == 'move_product')
async def handle_move_product(callback: CallbackQuery, state: FSMContext):
    app = callback.message.bot.state
    user = await app.db.users.get(callback.from_user.id)
    if not user.is_admin:
        return

    await send_product_list(await app.db.products.get_all(), callback)
    await callback.message.answer(WRITE_PRODUCT_ID)
    await state.set_state(ProductMove.id_state)


@move_product_router.message(ProductMove.id_state)
async def process_move_product_id(message: Message, state: FSMContext):
    try:
        product_id = int(message.text)
    except ValueError:
        await message.answer(MUST_BE_INT)
        return

    await state.update_data(product_id=product_id)
    await message.answer(CHOOSE_CATEGORY)
    await state.set_state(ProductMove.choice_state)


@move_product_router.message(ProductMove.choice_state)
async def process_move_product_choice(message: Message, state: FSMContext):
    app = message.bot.state
    data = await state.get_data()
    product_id = data.get('product_id')

    try:
        choice = int(message.text)
        if choice not in (1, 2, 3, 4):
            raise ValueError
    except ValueError:
        await message.answer(MUST_BE_CATEGORY)
        return

    status = STATUS_MAP[choice]
    await app.db.products.change_status(product_id, status)
    await message.answer(PRODUCT_MOVED.format(product_id, choice))
    await state.clear()
