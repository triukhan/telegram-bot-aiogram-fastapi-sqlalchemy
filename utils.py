import logging
import sys

from aiogram.types import User, InlineKeyboardButton, InlineKeyboardMarkup

from button_texts import ALL_ORDERS, MAKE_SPAM, ADD_PRODUCT, DELETE_PRODUCT, MOVE_PRODUCT, EDIT_PRODUCT, ALL_CHATS


def get_logger(name: str):
    logger_instance = logging.getLogger(name)
    if not logger_instance.hasHandlers():
        logger_instance.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger_instance.addHandler(handler)
    return logger_instance


class BotLogger(logging.Logger):
    def __init__(self):
        super().__init__('TelegramBot')
        self.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
        self.addHandler(handler)

    def log_user(self, action: str, user: User):
        self.info(
            f'{action} click - first_name: {user.first_name} last_name: {user.last_name} '
            f'username: {user.username} id: {user.id}'
        )


def get_admin_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=ALL_ORDERS, callback_data='all_orders')],
        [InlineKeyboardButton(text=MAKE_SPAM, callback_data='make_broadcast')],
        [InlineKeyboardButton(text=ADD_PRODUCT, callback_data='make_product')],
        [InlineKeyboardButton(text=DELETE_PRODUCT, callback_data='remove_product')],
        [InlineKeyboardButton(text=MOVE_PRODUCT, callback_data='move_product')],
        [InlineKeyboardButton(text=EDIT_PRODUCT, callback_data='edit_product')],
        [InlineKeyboardButton(text=ALL_CHATS, callback_data='all_supports')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


logger = BotLogger()
