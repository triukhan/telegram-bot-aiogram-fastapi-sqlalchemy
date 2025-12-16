import os
from datetime import datetime
import aiohttp

from api.wayforpay.utils import generate_signature, BASE_PAYLOAD, BASE_INVOICE
from utils import logger

WFP_REGULAR_URL = 'https://api.wayforpay.com/regularApi'
WFP_INVOICE_URL = 'https://api.wayforpay.com/api'
SERVICE_URL = os.getenv('SERVICE_URL')


class WayForPay:
    def __init__(self):
        self.url = WFP_REGULAR_URL

    async def post_request(self, payload: dict, url: str | None = None) -> dict:
        async with aiohttp.ClientSession() as session:
            logger.info(f'WFP <- POST {payload}')
            async with session.post(url or self.url, json=payload) as resp:
                logger.info(f'WFP -> {await resp.text()}')
                return await resp.json()

    async def check_payment_status(self, order_reference: str):
        payload = BASE_PAYLOAD.copy()
        payload['requestType'] = 'STATUS'
        payload['orderReference'] = order_reference

        return await self.post_request(payload)

    async def unsubscribe(self, order_reference: str):
        payload = BASE_PAYLOAD.copy()
        payload['requestType'] = 'REMOVE'
        payload['orderReference'] = order_reference

        return await self.post_request(payload)

    async def generate_invoice(self, user_id: int, name: str, price: int, period: None | str = None):
        if period is None:
            currency = 'EUR'
            service_endpoint = '/products-callback'
            order_reference = f'P{int(datetime.now().timestamp())}'
        else:
            currency = 'USD'
            service_endpoint = '/wayforpay-callback'
            order_reference = f'{user_id}_{int(datetime.now().timestamp())}'

        request_data = {
            **BASE_INVOICE,
            'currency': currency,
            'orderReference': order_reference,
            'orderDate': int(datetime.now().timestamp()),
            'amount': price,
            'productName': [name],
            'productCount': [1],
            'productPrice': [price],
            'clientFirstName': str(user_id),
            'clientEmail': f'user_{user_id}@fake.email',
            'serviceUrl': SERVICE_URL + service_endpoint,
            'clientAccountId': str(user_id),
        }

        if period is not None:
            request_data['regularMode'] = period
            request_data['regularAmount'] = price

        request_data['merchantSignature'] = generate_signature(request_data)

        response = await self.post_request(request_data, WFP_INVOICE_URL)

        if response.get('reasonCode') == 1100:
            return response['invoiceUrl']
        else:
            raise Exception(f'WFP Error: {response}')