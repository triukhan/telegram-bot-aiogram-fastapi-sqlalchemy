from fastapi import APIRouter, Request, HTTPException
from starlette.responses import JSONResponse

from api.zoom.utils import verify_zoom_signature, event_url_validation
from zoneinfo import ZoneInfo

from app import App
from texts import ZOOM_LINK
from utils import logger

router = APIRouter(prefix='/zoom-callback')
KYIV = ZoneInfo('Europe/Kyiv')


@router.post('')
async def zoom_callback(request: Request):
    data = await request.json()
    timestamp, signature = request.headers.get('x-zm-request-timestamp'), request.headers.get('x-zm-signature')
    app: App = request.app.state.app

    if data.get('event') == 'endpoint.url_validation':
        logger.info(f'ZOOM -> {data}')
        return await zoom_response(content=event_url_validation(data))

    if not verify_zoom_signature(signature, timestamp, await request.body()):
        raise HTTPException(status_code=401, detail='Invalid signature')

    if data.get('event') == 'recording.completed':
        rec_object = data['payload']['object']
        duration = rec_object.get('duration', 0)
        topic = rec_object.get('topic', '').lower()
        logger.info(f'ZOOM -> event: {data.get('event')} - topic: {topic} - duration: {duration}')

        if duration > 15 and 'yoga' in topic:
            text = ZOOM_LINK.format(rec_object.get('share_url'), rec_object.get('password'))
            await app.bot.send_to_channel(text, parse_mode='HTML', disable_web_page_preview=True)
            logger.info('recording is valid - sent to chat')
        else:
            logger.info('recording is too short')

        return await zoom_response()

    return await zoom_response(content={'status': 'ignored - not recording.completed'})


async def zoom_response(content: dict | None = None):
    content = content if content is not None else {'status': 'ok'}
    logger.info(f'ZOOM <- {content}')
    return JSONResponse(content=content)
