import logging
from collections import defaultdict
from typing import Callable, Dict, Any, Awaitable, Union, Set, Optional

import asyncio
from aiogram import BaseMiddleware
from aiogram.types import Message, Update
from aiogram.exceptions import TelegramRetryAfter
from config import bot_cfg


class AutoDeleteMessagesMiddleware(BaseMiddleware):
    def __init__(self):
        self.message_ids: Dict[int, Set[int]] = defaultdict(set)  # chat_id -> message_ids
        self.tasks: Dict[int, asyncio.Task] = {}                  # chat_id -> deletion task
        logging.info(f"Middleware {self.__class__.__name__} started")

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Union[Message, tuple[Message, Message]]]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        if event.inline_query:
            return await handler(event, data)

        message = self._extract_message(event)
        if message:
            self._ensure_deletion_task(message.chat.id, message)

        answer = await handler(event, data)
        if isinstance(answer, tuple):
            for msg in answer:
                self._ensure_deletion_task(msg.chat.id, msg)
        if isinstance(answer, Message):
            self._ensure_deletion_task(answer.chat.id, answer)

    @staticmethod
    def _extract_message(event: Update) -> Optional[Message]:
        if event.message:
            return event.message
        if event.callback_query.message:
            return event.callback_query.message
        return None

    def _ensure_deletion_task(self, chat_id: int, message: Message) -> None:
        self.message_ids[chat_id].add(message.message_id)

        if chat_id in self.tasks:
            self.tasks[chat_id].cancel()
        self.tasks[chat_id] = asyncio.create_task(self._schedule_deletion(chat_id, message))

    async def _schedule_deletion(self, chat_id: int, message: Message) -> None:
        await asyncio.sleep(bot_cfg.ttl)

        while self.message_ids[chat_id]:
            message_id = self.message_ids[chat_id].pop()
            try:
                await message.bot.delete_message(chat_id, message_id)
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after)
                await message.bot.delete_message(chat_id, message_id)
            except Exception as e:
                logging.error(f"Failed to delete message {message_id} in chat {chat_id}: {e}")
        self.tasks.pop(chat_id, None)   # noqa
