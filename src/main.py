from __future__ import annotations

import asyncio
import logging
from logging import Logger
from typing import Final

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from .config import BOT_CFG
from .database import db
from .handlers import handler_routers
from .middleware import AutoDeleteMessagesMiddleware

BOT: Final[Bot] = Bot(token=BOT_CFG.token)
DISPATCHER: Final[Dispatcher] = Dispatcher()
LOGGER: Final[Logger] = logging.getLogger(__name__)


async def on_startup() -> None:
    LOGGER.info("Bot is starting up...")
    await db.initialize()
    # DISPATCHER.fsm.storage = db.nosql.storage


async def on_shutdown() -> None:
    LOGGER.info("Bot is shutting down...")
    await db.close()
    await BOT.session.close()


def setup_dispatcher() -> None:
    DISPATCHER.startup.register(on_startup)
    DISPATCHER.shutdown.register(on_shutdown)
    DISPATCHER.update.middleware.register(AutoDeleteMessagesMiddleware())
    DISPATCHER.include_routers(*handler_routers)


async def set_webhook() -> None:
    expected_url = f"{BOT_CFG.web_server_url}{BOT_CFG.webhook_path}"

    current_webhook = await BOT.get_webhook_info()
    if not current_webhook.url:
        await BOT.set_webhook(expected_url, secret_token=BOT_CFG.webhook_secret)
        LOGGER.info("Webhook has been set.")
        return

    should_update = current_webhook.url != expected_url
    if should_update:
        LOGGER.info("Webhook needs to be updated. Setting new webhook...")
        await BOT.set_webhook(url=expected_url, secret_token=BOT_CFG.webhook_secret)
    else:
        LOGGER.info("Webhook is already set correctly.")


def start_webhook_mode() -> None:
    DISPATCHER.startup.register(set_webhook)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(DISPATCHER, BOT, secret_token=BOT_CFG.webhook_secret)
    webhook_requests_handler.register(app, path=BOT_CFG.webhook_path)
    setup_application(app, DISPATCHER, bot=BOT)
    web.run_app(app, host=BOT_CFG.web_server_host, port=BOT_CFG.web_server_port)


async def start_polling_mode() -> None:
    current_webhook = await BOT.get_webhook_info()
    if current_webhook.url:
        await BOT.delete_webhook()

    await DISPATCHER.start_polling(BOT)  # pyright: ignore[reportUnknownMemberType]


async def main() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    setup_dispatcher()
    try:
        if BOT_CFG.mode == "webhook":
            start_webhook_mode()
        elif BOT_CFG.mode == "polling":
            await start_polling_mode()
    except asyncio.CancelledError:
        LOGGER.info("Bot has been manually stopped.")


if __name__ == "__main__":
    asyncio.run(main())
