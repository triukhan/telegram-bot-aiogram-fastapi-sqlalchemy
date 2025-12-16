from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from texts import MUST_BE_INT, WRITE_PRODUCT_NAME, WRITE_PRODUCT_DESCR, WRITE_PRODUCT_PRICE, WRITE_PRODUCT_LINK, \
    PRODUCT_SAVED

add_product_router = Router()


class ProductForm(StatesGroup):
    price = State()
    name = State()
    description = State()
    link = State()


@add_product_router.callback_query(lambda c: c.data == 'make_product')
async def handle_make_product(callback: CallbackQuery, state: FSMContext):
    app = callback.message.bot.state
    user = await app.db.users.get(callback.from_user.id)
    if not user.is_admin:
        return

    await callback.message.answer(WRITE_PRODUCT_PRICE)
    await state.set_state(ProductForm.price)


@add_product_router.message(ProductForm.price)
async def process_price(message: Message, state: FSMContext):
    try:
        price = int(message.text)
    except ValueError:
        await message.answer(MUST_BE_INT)
        return

    await state.update_data(price=price)
    await message.answer(WRITE_PRODUCT_NAME)
    await state.set_state(ProductForm.name)


@add_product_router.message(ProductForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(WRITE_PRODUCT_DESCR)
    await state.set_state(ProductForm.description)


@add_product_router.message(ProductForm.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(WRITE_PRODUCT_LINK)
    await state.set_state(ProductForm.link)


@add_product_router.message(ProductForm.link)
async def process_link(message: Message, state: FSMContext):
    await state.update_data(link=message.text)
    app = message.bot.state
    data = await state.get_data()
    price, name, description, link = data['price'], data['name'], data['description'], data['link']

    await app.db.products.add(name, price, description, link)
    await message.answer(PRODUCT_SAVED.format(name, price, description, link))
    await state.clear()
