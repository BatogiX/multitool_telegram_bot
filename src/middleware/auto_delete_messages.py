from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import Message, Update

from config import BOT_CFG

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)


class AutoDeleteMessagesMiddleware(BaseMiddleware):
    def __init__(self):
        self.message_ids: dict[int, set[int]] = defaultdict(set)  # chat_id -> message_ids
        self.tasks: dict[int, asyncio.Task] = {}  # chat_id -> deletion task
        logger.info(f"Middleware {self.__class__.__name__} started")

    async def __call__(
        self,
        handler: Callable[[Update, dict], Awaitable[Message | tuple[Message, Message]]],
        event: Update,
        data: dict[str, Any],
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
    def _extract_message(event: Update) -> Message | None:
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
        await asyncio.sleep(BOT_CFG.ttl)

        while self.message_ids[chat_id]:
            message_id = self.message_ids[chat_id].pop()
            try:
                await message.bot.delete_message(chat_id, message_id)
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after)
                await message.bot.delete_message(chat_id, message_id)
            except Exception as e:
                logger.exception(f"Failed to delete message {message_id} in chat {chat_id}: {e}")
        self.tasks.pop(chat_id)
