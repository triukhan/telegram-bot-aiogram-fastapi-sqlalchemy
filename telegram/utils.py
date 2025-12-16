import enum
from functools import wraps
from aiogram.types import Message, CallbackQuery

from texts import PRODUCT_LIST, PRODUCT_ITEM

MAX_MESSAGE_LENGTH = 4096


class ProductStatus(enum.Enum):
    ACTIVE = 'ACTIVE'
    SCHOOL = 'SCHOOL'
    RECORDS = 'RECORDS'
    ARCHIVED = 'ARCHIVED'


def private_only(handler):
    @wraps(handler)
    async def wrapper(message: Message, *args, **kwargs):
        if message.chat.type != 'private':
            return
        return await handler(message, *args, **kwargs)
    return wrapper


async def send_product_list(products: list, callback: CallbackQuery):
    text = PRODUCT_LIST
    for p in products:
        text += PRODUCT_ITEM.format(p.id, p.name, p.price, p.link)

    for i in range(0, len(text), MAX_MESSAGE_LENGTH):
        chunk = text[i:i + MAX_MESSAGE_LENGTH]
        await callback.message.answer(chunk, parse_mode=None)
