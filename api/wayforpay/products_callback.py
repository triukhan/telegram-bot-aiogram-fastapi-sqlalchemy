from fastapi import APIRouter, Request

from api.wayforpay.utils import generate_ok, validate_signature
from app import App
from db.models import User

from texts import DECLINED, LINK_WILL_BE_LATER, PRODUCT_LINK, PRODUCT_SUCCESS_PAYMENT
from utils import logger

router = APIRouter(prefix='/products-callback')


@router.post('')
async def products_callback(request: Request):
    data = await request.json()
    logger.info(f'WFP -> {data}')
    app: App = request.app.state.app
    order_reference, status = validate_signature(data)
    user_id = int(data['clientAccountId'])
    product_name = data['products'][0]['name']

    if (user := await app.db.users.get(user_id)) is None:
        user = await app.db.users.add(user_id)
    if status == 'Approved':
        await process_successful_payment(app, user, order_reference, product_name)
    else:
        await app.bot.save_send_message(user_id, DECLINED, reply_markup=await app.get_main_keyboard(user))
        await app.db.orders.remove(order_reference)

    return generate_ok(order_reference)


async def process_successful_payment(app: App, user: User, order_reference: str, product_name: str):
    product = await app.db.products.get_by_name(product_name)
    await app.db.orders.add(int(user.id), int(product.id), order_reference)
    link_text = LINK_WILL_BE_LATER if product.link == '.' else PRODUCT_LINK.format(product.link)

    await app.bot.save_send_message(
        user.id, PRODUCT_SUCCESS_PAYMENT.format(link_text), reply_markup=await app.get_main_keyboard(user)
    )
