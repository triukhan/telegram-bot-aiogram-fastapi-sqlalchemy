from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup

from button_texts import ANSWERS, NO_ANSWER_QUESTION, CHANGE_PAYMENT_CARD, HOW_TO_RECEIVE_PRODUCT, WILL_BE_RECORD, \
    HOW_TO_PAY
from telegram.utils import private_only
from texts import QUESTION_LIST, HOW_TO_PAY_ANSWER, RECORD_ANSWER, RECEIVE_PRODUCT_ANSWER, IF_NOT_ACCESS_ANSWER, \
    SUPPORT_ANSWER
from utils import logger

answers_router = Router()


@answers_router.message(F.text == ANSWERS)
@private_only
async def handle_ask_question(message: Message):
    tg_user = message.from_user
    logger.log_user('handle_ask_question', tg_user)

    keyboard_list = [
        [InlineKeyboardButton(text=HOW_TO_PAY, callback_data='how_to_pay')],
        [InlineKeyboardButton(text=WILL_BE_RECORD, callback_data='will_be_record')],
        [InlineKeyboardButton(text=HOW_TO_RECEIVE_PRODUCT, callback_data='how_to_receive_product')],
        [InlineKeyboardButton(text=CHANGE_PAYMENT_CARD, callback_data='what_if_not_access')],
        [InlineKeyboardButton(text=NO_ANSWER_QUESTION, callback_data='ask_support')]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_list, resize_keyboard=True)
    await message.answer(QUESTION_LIST, reply_markup=keyboard, parse_mode='Markdown')


@answers_router.callback_query(lambda c: c.data == 'how_to_pay')
async def handle_how_to_pay(callback: CallbackQuery):
    await callback.message.answer(HOW_TO_PAY_ANSWER)


@answers_router.callback_query(lambda c: c.data == 'will_be_record')
async def handle_will_be_record(callback: CallbackQuery):
    await callback.message.answer(RECORD_ANSWER)


@answers_router.callback_query(lambda c: c.data == 'how_to_receive_product')
async def handle_how_to_receive_product(callback: CallbackQuery):
    await callback.message.answer(RECEIVE_PRODUCT_ANSWER)


@answers_router.callback_query(lambda c: c.data == 'what_if_not_access')
async def handle_what_if_not_access(callback: CallbackQuery):
    await callback.message.answer(IF_NOT_ACCESS_ANSWER)


@answers_router.callback_query(lambda c: c.data == 'ask_support')
async def handle_ask_support(callback: CallbackQuery):
    await callback.message.answer(SUPPORT_ANSWER)
