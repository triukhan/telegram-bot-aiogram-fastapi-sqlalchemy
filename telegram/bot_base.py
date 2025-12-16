from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import os

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, BotCommand, BotCommandScopeAllPrivateChats
from dotenv import load_dotenv
from telegram.routers.message_routers import all_routers
from texts import MENU
from utils import logger

load_dotenv()

CHAT_ID = int(os.getenv('CHAT_ID'))
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
TG_TOKEN = os.getenv('TG_TOKEN')


class TelegramBot(Bot):
    def __init__(self):
        super().__init__(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.dp = Dispatcher(storage=MemoryStorage())
        self.connect_routers()

    def connect_routers(self):
        for router in all_routers:
            self.dp.include_router(router)

    async def start(self):
        await self.delete_webhook(drop_pending_updates=True)
        await self.set_my_commands(
            commands=[BotCommand(command='menu', description=MENU)],
            scope=BotCommandScopeAllPrivateChats()
        )
        await self.dp.start_polling(self)


class AppBotBase(TelegramBot):
    def __init__(self):
        super().__init__()
        self.chat_id = CHAT_ID
        self.channel_id = CHANNEL_ID

    async def kick_from_chat_and_channel(self, user_id: int):
        try:
            await self.ban_chat_member(CHAT_ID, user_id)
            await self.unban_chat_member(CHAT_ID, user_id)

            await self.ban_chat_member(CHANNEL_ID, user_id)
            await self.unban_chat_member(CHANNEL_ID, user_id)
            logger.info(f'{user_id} was kicked from chat and channel')
        except Exception as e:
            logger.error(f'sending to user {user_id}: {e}')

    async def generate_invite_links(self) -> tuple[str, str]:
        expire_date = int(datetime.now().timestamp()) + 3600
        parameters = {'member_limit': 1, 'creates_join_request': False, 'expire_date': expire_date}

        chat_link = await self.create_chat_invite_link(chat_id=self.chat_id, **parameters)
        channel_link = await self.create_chat_invite_link(chat_id=self.channel_id, **parameters)

        return chat_link.invite_link, channel_link.invite_link

    async def save_send_message(self, chat_id: int, text: str, reply_markup: ReplyKeyboardMarkup | InlineKeyboardMarkup | None = None):
        try:
            await self.send_message(chat_id, text, reply_markup=reply_markup)
        except TelegramForbiddenError as err:
            logger.info(err)

    async def send_to_channel(self, text: str, **kwargs):
        await self.send_message(chat_id=CHANNEL_ID, text=text, **kwargs)
