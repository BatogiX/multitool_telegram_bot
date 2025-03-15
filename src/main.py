import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from config import bot_cfg, db_manager
from handlers import handlers_router


async def on_startup() -> tuple[Dispatcher, Bot]:
    logging.info("Bot is starting up...")
    await db_manager.initialize()

    dispatcher = Dispatcher(storage=db_manager.key_value_db.storage)
    dispatcher.include_router(handlers_router)
    bot = Bot(token=bot_cfg.token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))
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
