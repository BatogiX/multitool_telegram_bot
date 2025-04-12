import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from database import db_manager
from config import bot_cfg
from handlers import handlers_router
from middleware import AutoDeleteMessagesMiddleware

bot = Bot(token=bot_cfg.token)
dispatcher = Dispatcher()


def setup_dispatcher() -> None:
    dispatcher.startup.register(on_startup)
    dispatcher.shutdown.register(on_shutdown)
    dispatcher.update.middleware.register(AutoDeleteMessagesMiddleware())
    dispatcher.include_router(handlers_router)


async def on_startup() -> None:
    logging.info("Bot is starting up...")
    await db_manager.initialize()
    dispatcher.fsm.storage = db_manager.key_value_db.storage


async def on_shutdown() -> None:
    logging.info("Bot is shutting down...")
    await bot.session.close()
    await db_manager.close()


async def start_polling_mode() -> None:
    setup_dispatcher()

    current_webhook = await bot.get_webhook_info()
    if current_webhook.url:
        await bot.delete_webhook()

    try:
        await dispatcher.start_polling(bot)
    except asyncio.CancelledError:
        logging.info("Bot has been manually stopped.")


async def set_webhook() -> None:
    expected_url = f"{bot_cfg.webhook_url}{bot_cfg.webhook_path}"

    current_webhook = await bot.get_webhook_info()
    if not current_webhook.url:
        await bot.set_webhook(expected_url, secret_token=bot_cfg.webhook_secret)
        logging.info("Webhook has been set.")
        return

    should_update = current_webhook.url != expected_url
    if should_update:
        logging.info("Webhook needs to be updated. Setting new webhook...")
        await bot.set_webhook(
            url=expected_url,
            secret_token=bot_cfg.webhook_secret
        )
    else:
        logging.info("Webhook is already set correctly.")


def start_webhook_mode() -> None:
    setup_dispatcher()
    dispatcher.startup.register(set_webhook)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dispatcher, bot=bot, secret_token=bot_cfg.webhook_secret)
    webhook_requests_handler.register(app, path=bot_cfg.webhook_path)
    setup_application(app, dispatcher, bot=bot)
    web.run_app(app, host=bot_cfg.web_server_host, port=bot_cfg.web_server_port)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    if bot_cfg.webhook_url:
        start_webhook_mode()
    else:
        asyncio.run(start_polling_mode())
