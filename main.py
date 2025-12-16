from contextlib import asynccontextmanager, suppress

import uvicorn
from fastapi import FastAPI
import asyncio

from api.wayforpay.wayforpay_callback import router as wayforpay_router
from api.wayforpay.products_callback import router as products_router
from api.zoom.webhook import router as zoom_router
from app import App
from services.scheduler import start_scheduler
from telegram.routers.admin_routers.make_broadcast import message_scheduler


@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    fastapi.state.app = await App.create()
    bot_task = asyncio.create_task(fastapi.state.app.bot.start())
    start_scheduler(fastapi.state.app)
    message_scheduler.start()

    yield

    bot_task.cancel()
    with suppress(asyncio.CancelledError):
        await bot_task

fastapi_app = FastAPI(lifespan=lifespan)
fastapi_app.include_router(wayforpay_router)
fastapi_app.include_router(products_router)
fastapi_app.include_router(zoom_router)


async def run_api():
    config = uvicorn.Config(fastapi_app, host='0.0.0.0', port=8080)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == '__main__':
    asyncio.run(run_api())
