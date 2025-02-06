import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from config import TOKEN, db_manager
from handlers import router as handlers_router


async def on_startup() -> tuple[Bot, Dispatcher]:
    logging.info("Bot is starting up...")
    await db_manager.initialize()

    dispatcher = Dispatcher(storage=RedisStorage(await db_manager.key_value_db.connect()))
    dispatcher.include_router(handlers_router)
    bot = Bot(token=TOKEN, default_bot_properties=DefaultBotProperties(parse_mode=ParseMode.HTML))

    return bot, dispatcher


async def on_shutdown(bot: Bot) -> None:
    logging.info("Bot is shutting down...")
    await bot.session.close()
    await db_manager.close()


async def main() -> None:
    bot, dispatcher = await on_startup()
    try:
        await dispatcher.start_polling(bot)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logging.info("Bot has been manually stopped.")
    finally:
        await on_shutdown(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    asyncio.run(main())
