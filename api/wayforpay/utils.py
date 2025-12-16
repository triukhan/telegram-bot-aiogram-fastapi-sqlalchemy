import hashlib
import hmac
import os
from fastapi import HTTPException
from datetime import datetime

from texts import REMOVED, REFUND, SUSPENDED
from dotenv import load_dotenv

from utils import logger

load_dotenv()

MERCHANT_ACCOUNT = os.getenv('MERCHANT_ACCOUNT')
MERCHANT_PASSWORD = os.getenv('MERCHANT_PASSWORD')
MERCHANT_DOMAIN_NAME = os.getenv('MERCHANT_DOMAIN_NAME')
MERCHANT_SECRET_KEY = os.getenv('MERCHANT_SECRET_KEY').encode('utf-8')
NEGATIVE_TEXTS_MAP = {'Removed': REMOVED, 'Refunded': REFUND, 'Suspended': SUSPENDED}
BASE_PAYLOAD = {
    'merchantAccount': MERCHANT_ACCOUNT,
    'merchantPassword': MERCHANT_PASSWORD,
    'apiVersion': 1,
}
BASE_INVOICE = {
    'transactionType': 'CREATE_INVOICE',
    'merchantAccount': MERCHANT_ACCOUNT,
    'merchantAuthType': 'SimpleSignature',
    'merchantDomainName': MERCHANT_DOMAIN_NAME,
    'language': 'UA',
    'apiVersion': 1,
    'orderTimeout': 3600,
    'regularBehavior': 'preset',
    'regularCount': 100,
    'paymentSystems': 'card;googlePay;applePay;privat24;masterPass;payPartsMono:2,3,7,10;payParts:2,3,7,10;payPartsPr'
                      'ivat:2,3,7,10;OnusInstallment:2,3,7,10'
}


def generate_ok(order_reference):
    response_time = int(datetime.now().timestamp())
    response_signature_str = f'{order_reference};accept;{response_time}'.encode('utf-8')
    response_signature = hmac.new(MERCHANT_SECRET_KEY, response_signature_str, hashlib.md5).hexdigest()
    response = {
        'orderReference': order_reference, 'status': 'accept', 'time': response_time, 'signature': response_signature
    }
    logger.info(f'WFP <- OK {response}')
    return response


def generate_signature(request_data: dict) -> str:
    sign_list = [
        request_data.get('merchantAccount'),
        request_data.get('merchantDomainName'),
        request_data.get('orderReference'),
        str(request_data.get('orderDate')),
        str(request_data.get('amount')),
        request_data.get('currency'),
        request_data.get('productName')[0],
        str(request_data.get('productCount')[0]),
        str(request_data.get('amount')),
    ]
    sign_string = ';'.join(sign_list).encode('utf-8')
    return hmac.new(MERCHANT_SECRET_KEY, sign_string, hashlib.md5).hexdigest()


def validate_signature(data):
    if data.get('status') and data.get('processingDate'):
        signature_fields = (
            data.get('merchantAccount', ''),
            data.get('orderReference', ''),
            str(data.get('processingDate', '')),
            data.get('status', ''),
            str(data.get('reasonCode', '')),
        )
    else:
        signature_fields = (
            data.get('merchantAccount', ''),
            data.get('orderReference', ''),
            str(data.get('amount', '')),
            data.get('currency', ''),
            data.get('authCode', ''),
            data.get('cardPan', ''),
            data.get('transactionStatus', ''),
            str(data.get('reasonCode', ''))
        )

    signature_str = ';'.join(signature_fields).encode('utf-8')
    expected_signature = hmac.new(MERCHANT_SECRET_KEY, signature_str, hashlib.md5).hexdigest()

    if expected_signature != data.get('merchantSignature'):
        raise HTTPException(status_code=403, detail='Invalid signature')

    order_reference = data['orderReference']
    status = data.get('transactionStatus') or data.get('status')

    return order_reference, status

