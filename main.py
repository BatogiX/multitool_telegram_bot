import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from src.config import bot_config, db_manager
from src.handlers import router as handlers_router


async def on_startup() -> tuple[Dispatcher, Bot]:
    logging.info("Bot is starting up...")
    await db_manager.initialize()

    dispatcher = Dispatcher(storage=RedisStorage(await db_manager.key_value_db.connect()))
    dispatcher.include_router(handlers_router)
    bot = Bot(token=bot_config.token, default_bot_properties=DefaultBotProperties(parse_mode=ParseMode.HTML))

    return dispatcher, bot


async def on_shutdown(bot: Bot) -> None:
    logging.info("Bot is shutting down...")
    await bot.session.close()
    await db_manager.close()


async def main() -> None:
    dispatcher, bot = await on_startup()
    try:
        await dispatcher.start_polling(bot)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logging.info("Bot has been manually stopped.")
    finally:
        await on_shutdown(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    asyncio.run(main())
