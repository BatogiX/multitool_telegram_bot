import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from config import TOKEN_ENV_VAR
from db.redis import RedisManager
from handlers import router as handlers_router


async def on_startup() -> tuple[Bot, Dispatcher]:
    logging.info("Bot is starting up...")

    if not TOKEN_ENV_VAR:
        raise ValueError(f"TOKEN_ENV_VAR is not set in the environment variables (.env)!")

    dispatcher = Dispatcher(storage=RedisStorage(redis=await RedisManager.connect()))
    dispatcher.include_router(handlers_router)
    bot = Bot(token=TOKEN_ENV_VAR, default_bot_properties=DefaultBotProperties(parse_mode=ParseMode.HTML))

    return bot, dispatcher


async def on_shutdown(bot: Bot) -> None:
    logging.info("Bot is shutting down...")
    await bot.session.close()
    if RedisManager.connection:
        await RedisManager.disconnect()


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
