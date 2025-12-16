from button_texts import SCHOOL, BACK_TO_PRODUCTS, BACK_TO_MAIN, WEBINAR_RECS
from telegram.utils import private_only
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from texts import FIRST_MESSAGE, MENU
from utils import logger
from aiogram.filters import CommandStart, Command

user_other_router = Router()


@user_other_router.message(CommandStart())
@private_only
async def cmd_start(message: Message):
    tg_user, app = message.from_user, message.bot.state
    logger.log_user('start', tg_user)
    user = await app.get_or_create_user(tg_user.id)

    first_message = 'menu' if user.is_admin else FIRST_MESSAGE
    await message.answer(first_message, reply_markup=await app.get_main_keyboard(user))


@user_other_router.message(Command('menu'))
@private_only
async def menu_cmd(message: Message):
    tg_user, app = message.from_user, message.bot.state
    logger.log_user('menu', tg_user)
    user = await app.get_or_create_user(tg_user.id)

    await message.answer(MENU, reply_markup=await app.get_main_keyboard(user))


@user_other_router.message(F.text == SCHOOL)
async def handle_click_school(message: CallbackQuery):
    app = message.bot.state
    logger.log_user(f'school', message.from_user)
    await message.answer(SCHOOL, reply_markup=await app.get_school_keyboard_with_products(), parse_mode='Markdown')


@user_other_router.message(F.text == BACK_TO_PRODUCTS)
@private_only
async def handle_click_back_school(message: CallbackQuery):
    app = message.bot.state
    await message.answer(
        BACK_TO_PRODUCTS, reply_markup=await app.get_school_keyboard_with_products(), parse_mode='Markdown'
    )


@user_other_router.message(F.text == BACK_TO_MAIN)
@private_only
async def handle_click_back_menu(message: CallbackQuery):
    app = message.bot.state
    user = await app.db.users.get(message.from_user.id)
    await message.answer(BACK_TO_MAIN, reply_markup=await app.get_main_keyboard(user), parse_mode='Markdown')


@user_other_router.message(F.text == WEBINAR_RECS)
@private_only
async def handle_click_back_school(message: CallbackQuery):
    app = message.bot.state
    await message.answer(
        BACK_TO_MAIN, reply_markup=await app.get_records_keyboard_with_products(), parse_mode='Markdown'
    )

