import logging
from collections import defaultdict
from typing import Callable, Dict, Any, Awaitable, Union, Set

import asyncio
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, Update, CallbackQuery
from aiogram.exceptions import TelegramRetryAfter
from config import bot_cfg


class AutoDeleteMessagesMiddleware(BaseMiddleware):
    def __init__(self):
        self.message_ids: Dict[int, Set[int]] = defaultdict(set)  # chat_id -> message_ids
        self.tasks: Dict[int, asyncio.Task] = {}                  # user_id -> deletion task
        logging.info(f"Middleware {self.__class__.__name__} started")

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        message = self.extract_message(event)
        if message:
            self.message_ids[message.chat.id].add(message.message_id)
            self.ensure_deletion_task(message.chat.id, message)

        return await handler(event, data)

    @staticmethod
    def extract_message(event: Update) -> Union[Message, None]:
        if event.message:
            return event.message
        if event.callback_query and event.callback_query.message:
            return event.callback_query.message
        return None

    def ensure_deletion_task(self, chat_id: int, obj: Union[Message, CallbackQuery]):
        if chat_id in self.tasks:
            self.tasks[chat_id].cancel()
        self.tasks[chat_id] = asyncio.create_task(self.schedule_deletion(chat_id, obj))

    async def schedule_deletion(self, chat_id: int, obj: Union[Message, CallbackQuery]):
        await asyncio.sleep(bot_cfg.ttl)

        while self.message_ids[chat_id]:
            message_id = self.message_ids[chat_id].pop()
            try:
                await obj.bot.delete_message(chat_id, message_id)
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after)
                await obj.bot.delete_message(chat_id, message_id)
            except Exception as e:
                logging.error(e)
        self.tasks.pop(chat_id, None)   # noqa
