from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from button_texts import MANAGE_SUBSCRIPTION, WEBINAR_RECS, SUBSCRIPTION, HELP, MY_PRODUCTS, SCHOOL, ANSWERS, BACK_TO_MAIN
from db.models import Product
from telegram.bot_base import AppBotBase
from telegram.utils import ProductStatus


class AppBot(AppBotBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_keyboard_with_products(products: list, user_orders: list, is_subscribed: bool):
        final_keyboard = []
        final_keyboard.extend(get_product_buttons(products))

        if is_subscribed:
            final_keyboard.append([KeyboardButton(text=MANAGE_SUBSCRIPTION), KeyboardButton(text=WEBINAR_RECS)])
        else:
            final_keyboard.append([KeyboardButton(text=SUBSCRIPTION), KeyboardButton(text=WEBINAR_RECS)])

        final_keyboard.append([KeyboardButton(text=SCHOOL), KeyboardButton(text=ANSWERS)])

        if user_orders:
            final_keyboard.append([KeyboardButton(text=HELP), KeyboardButton(text=MY_PRODUCTS)])
        else:
            final_keyboard.append([KeyboardButton(text=HELP)])

        return ReplyKeyboardMarkup(keyboard=final_keyboard, resize_keyboard=True)

    @staticmethod
    def get_school_keyboard(products: list):
        final_keyboard = get_product_buttons(products, ProductStatus.SCHOOL)
        final_keyboard.append([KeyboardButton(text=BACK_TO_MAIN)])
        return ReplyKeyboardMarkup(keyboard=final_keyboard, resize_keyboard=True,)

    @staticmethod
    def get_records_keyboard(products: list):
        final_keyboard = get_product_buttons(products, ProductStatus.RECORDS)
        final_keyboard.append([KeyboardButton(text=BACK_TO_MAIN)])
        return ReplyKeyboardMarkup(keyboard=final_keyboard, resize_keyboard=True,)


def get_product_buttons(products: list[Product], status: ProductStatus = ProductStatus.ACTIVE):
    products_buttons = []

    for product in products:
        if product.status == status:
            products_buttons.append([KeyboardButton(text=product.name)])
    return products_buttons
