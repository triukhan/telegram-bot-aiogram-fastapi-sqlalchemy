from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from telegram.utils import send_product_list
from texts import BROADCAST_SENT, BROADCAST, WRITE_PRODUCT_ID_TO_BROADCAST, MUST_BE_INT, WRITE_DATE_TO_BROADCAST, \
    WRONG_DATE_FORMAT, CONFIRM_DATE_BROADCAST, YES, BROADCAST_PLANNED, NO, BROADCAST_CANCELED, YES_OR_NO

broadcast_router = Router()
KYIV = ZoneInfo('Europe/Kyiv')
message_scheduler = AsyncIOScheduler(timezone=KYIV)


class BroadcastForm(StatesGroup):
    waiting_for_product = State()
    waiting_for_text = State()
    waiting_for_date = State()
    waiting_for_confirmation = State()


@broadcast_router.callback_query(lambda c: c.data == 'make_broadcast')
async def handle_broadcast(callback: CallbackQuery, state: FSMContext):
    app = callback.message.bot.state

    await send_product_list(await app.db.products.get_all(), callback)
    await callback.message.answer(WRITE_PRODUCT_ID_TO_BROADCAST)
    await state.set_state(BroadcastForm.waiting_for_product)


@broadcast_router.message(BroadcastForm.waiting_for_product)
async def save_product_handler(message: Message, state: FSMContext):
    if message.text == '-':
        await state.update_data(product_id=message.text)
    else:
        try:
            product_id = int(message.text)
        except ValueError:
            await message.answer(MUST_BE_INT)
            await state.clear()
            return
        await state.update_data(product_id=product_id)

    await message.answer(BROADCAST)
    await state.set_state(BroadcastForm.waiting_for_text)


@broadcast_router.message(BroadcastForm.waiting_for_text)
async def save_text_handler(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer(WRITE_DATE_TO_BROADCAST)
    await state.set_state(BroadcastForm.waiting_for_date)


@broadcast_router.message(BroadcastForm.waiting_for_date)
async def save_date_handler(message: Message, state: FSMContext):
    app = message.bot.state
    data = await state.get_data()

    if message.text == '-':
        await app.send_broadcast_message(data['text'], data['product_id'])
        await message.answer(BROADCAST_SENT.format(message.text))
        await state.clear()
        return
    else:
        try:
            send_time = datetime.strptime(message.text.strip(), '%Y-%m-%d %H:%M')
        except ValueError:
            await message.answer(WRONG_DATE_FORMAT)
            return

        await state.update_data(send_time=send_time)
        await message.answer(CONFIRM_DATE_BROADCAST.format(data['text'], send_time.strftime('%d %B %Y %H:%M')))
        await state.set_state(BroadcastForm.waiting_for_confirmation)


@broadcast_router.message(BroadcastForm.waiting_for_confirmation)
async def confirmation_handler(message: Message, state: FSMContext):
    app = message.bot.state
    answer = message.text.lower()

    if answer == YES:
        data = await state.get_data()
        send_time, text, product_id = data['send_time'], data['text'], data['product_id']

        message_scheduler.add_job(
            app.send_broadcast_message, 'date', run_date=send_time, args=[text, product_id]
        )
        await message.answer(
            BROADCAST_PLANNED.format(send_time.strftime('%d %B %Y %H:%M')), reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
    elif answer == NO:
        await message.answer(BROADCAST_CANCELED, reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer(YES_OR_NO)
