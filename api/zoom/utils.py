import hashlib
import hmac
import os

from dotenv import load_dotenv

load_dotenv()
ZOOM_SECRET_TOKEN = os.getenv('ZOOM').encode('utf-8')


def verify_zoom_signature(received_signature: str, timestamp: str, raw_body: bytes) -> bool:
    message = f'v0:{timestamp}:{raw_body.decode('utf-8')}'.encode('utf-8')
    hashed = hmac.new(ZOOM_SECRET_TOKEN, message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(received_signature, f'v0={hashed}')


def event_url_validation(data):
    plain_token = data['payload']['plainToken']
    exp_token = hmac.new(ZOOM_SECRET_TOKEN, plain_token.encode('utf-8'), hashlib.sha256).hexdigest()

    return {
        'plainToken': plain_token,
        'encryptedToken': exp_token
    }

