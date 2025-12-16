from telegram.routers.admin_routers.add_product import add_product_router
from telegram.routers.admin_routers.edit_product import edit_product_router
from telegram.routers.admin_routers.make_broadcast import broadcast_router
from telegram.routers.admin_routers.move_product import move_product_router
from telegram.routers.admin_routers.other import admin_other_router
from telegram.routers.admin_routers.remove_product import remove_product_router
from telegram.routers.support_routers.answers import answers_router
from telegram.routers.support_routers.chat import chat_router
from telegram.routers.user_routers.other import user_other_router
from telegram.routers.user_routers.product import user_product_router
from telegram.routers.user_routers.subscriptions import subscription_router


all_routers = [
    add_product_router,
    edit_product_router,
    move_product_router,
    remove_product_router,
    admin_other_router,
    broadcast_router,
    subscription_router,
    user_other_router,
    answers_router,
    user_product_router,
    chat_router,
]
