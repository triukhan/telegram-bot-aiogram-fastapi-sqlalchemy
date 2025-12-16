from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from button_texts import HELP, ADMIN_ANSWER, ADMIN_PAUSE, ADMIN_CLOSE
from telegram.utils import private_only
from texts import HELP_TEXT, SUPPORT_RECEIVED_QUESTION, INACTIVE_CHAT, NEW_CHAT, NO_ADMIN_TAKE, ADMIN_JOIN, ADMIN_SENT, \
    ADMIN_CONFIRM, PAUSE_CHAT, USER_CLOSED_CHAT, ADMIN_CLOSED_CHAT
from utils import logger

chat_router = Router()


class SupportState(StatesGroup):
    waiting_for_question = State()
    question_sent = State()


@chat_router.message(F.text == HELP)
@private_only
async def handle_support(message: Message, state: FSMContext):
    tg_user, app = message.from_user, message.bot.state
    await app.get_or_create_user(tg_user.id)
    await state.set_state(SupportState.waiting_for_question)
    logger.log_user('question', tg_user)

    await message.answer(HELP_TEXT)


@chat_router.message(SupportState.waiting_for_question)
@private_only
async def handle_ask_support(message: Message, state: FSMContext):
    tg_user, app = message.from_user, message.bot.state
    user = await app.db.users.get(tg_user.id)

    await app.db.support_chats.add(user_id=user.id)

    for admin in await app.db.users.get_admins():
        kb = InlineKeyboardBuilder()
        kb.row(
            InlineKeyboardButton(text=ADMIN_ANSWER, callback_data=f'support_reply:{user.id}'),
            InlineKeyboardButton(text=ADMIN_PAUSE, callback_data=f'support_pause:{user.id}'),
            InlineKeyboardButton(text=ADMIN_CLOSE, callback_data=f'support_close:{user.id}')
        )

        await message.bot.send_message(
            admin.user_id, NEW_CHAT.format(tg_user.id, tg_user.username, message.text), reply_markup=kb.as_markup()
        )

    await state.set_state(SupportState.question_sent)
    await message.answer(SUPPORT_RECEIVED_QUESTION)


@chat_router.callback_query(F.data.startswith('support_reply:'))
async def admin_take_chat(callback: CallbackQuery):
    app = callback.bot.state
    _, user_id = callback.data.split(':')
    user_id = int(user_id)
    chat = await app.db.support_chats.get(user_id)

    if not chat:
        return await callback.message.answer(INACTIVE_CHAT)
    await app.db.support_chats.assign_admin(user_id=user_id, admin_id=callback.from_user.id)

    user_storage_key = StorageKey(bot_id=callback.bot.id, chat_id=user_id, user_id=user_id)
    user_fsm = FSMContext(storage=callback.bot.dp.fsm.storage, key=user_storage_key)

    await user_fsm.set_state(SupportState.question_sent)
    await callback.message.answer(ADMIN_JOIN.format(user_id))


@chat_router.message(SupportState.question_sent)
@private_only
async def user_reply(message: Message):
    tg_user, app = message.from_user, message.bot.state
    chat = await app.db.support_chats.get_by_user(message.from_user.id)
    logger.log_user('user_reply', tg_user)

    if not chat.admin_id:
        await message.answer(NO_ADMIN_TAKE)
        return

    await message.bot.send_message(
        chat.admin_id, ADMIN_JOIN.format(message.from_user.username or message.from_user.id, message.text)
    )


@chat_router.message(F.chat.type == 'private')
async def admin_message(message: Message):
    app = message.bot.state
    chat = await app.db.support_chats.get_by_admin(message.from_user.id)

    if not chat:
        return

    await message.bot.send_message(chat.user_id, ADMIN_SENT.format(message.text))
    await message.answer(ADMIN_CONFIRM.format(chat.user_id))
    logger.info(f'sent: {chat.user_id} {message.text}')


@chat_router.callback_query(F.data.startswith('support_pause:'))
async def pause_chat(callback: CallbackQuery):
    app = callback.bot.state
    _, user_id = callback.data.split(':')
    user_id = int(user_id)

    await app.db.support_chats.pause(user_id)
    await callback.message.answer(PAUSE_CHAT.format(user_id))


@chat_router.callback_query(F.data.startswith('support_close:'))
async def close_chat(callback: CallbackQuery):
    app = callback.bot.state
    _, user_id = callback.data.split(':')
    user_id = int(user_id)

    user_storage_key = StorageKey(bot_id=callback.bot.id, chat_id=user_id, user_id=user_id)
    user_fsm = FSMContext(storage=callback.bot.dp.fsm.storage, key=user_storage_key)

    await user_fsm.clear()
    await app.db.support_chats.remove(user_id)

    await callback.bot.send_message(user_id, USER_CLOSED_CHAT)
    await callback.message.answer(ADMIN_CLOSED_CHAT)
