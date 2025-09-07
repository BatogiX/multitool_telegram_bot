from __future__ import annotations

import logging
from datetime import timedelta
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Final, cast, final, override

import orjson
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import ConnectionPool, Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from config import NOSQL_DB_CFG

from .base import AbstractNoSQLDriver, ExpireT

if TYPE_CHECKING:
    from redis.asyncio import Connection
    from redis.asyncio.client import CommandStackT, CommandT, Pipeline

logger = logging.getLogger(__name__)


class CommandKind(Enum):
    GET = auto()
    SET = auto()
    DEL = auto()


update_commands: Final = {CommandKind.SET.name, CommandKind.DEL.name}


@final
class RedisDriver(AbstractNoSQLDriver):
    """
    Implementation of a key-value store for Redis.
    """

    def __init__(self) -> None:
        self.redis = Redis(connection_pool=self._create_connection_pool(), decode_responses=True)
        self.storage = RedisStorage(
            redis=self.redis,
            state_ttl=NOSQL_DB_CFG.state_ttl,
            data_ttl=NOSQL_DB_CFG.data_ttl,
        )

    @override
    async def connect(self) -> None:
        try:
            await self.redis.ping()  # pyright: ignore[reportUnknownMemberType]
        except RedisConnectionError:
            logger.exception("Failed to connect to Redis")
            raise
        else:
            logger.info("Connected to Redis")

    @override
    def create_transaction(self) -> Pipeline:
        return self.redis.pipeline(transaction=True)

    @staticmethod
    def _json_commands(
        command_stack: CommandStackT,
    ) -> tuple[CommandStackT, tuple[str, ...], set[str], dict[int, CommandT]]:
        need_update_json_keys: set[str] = set()
        json_keys: set[str] = set()
        json_command_stack: dict[int, CommandT] = {}

        for i in range(len(command_stack) - 1, -1, -1):
            key = command_stack[i][0][1]

            if key.endswith(suffixies):
                command = command_stack.pop(i)
                json_command_stack[i] = command
                json_keys.add(str(key))

                cmd = command_stack[i][0][0]
                if cmd in update_commands:
                    need_update_json_keys.add(str(key))

        return command_stack, tuple(json_keys), need_update_json_keys, json_command_stack

    @staticmethod
    async def _execute_without_reset(
        transaction: Pipeline,
        *,
        raise_on_error: bool = True,
    ) -> list[Any]:
        # receive connection manually to GET json values from keys
        # and transmit this connection to .execute()
        conn = transaction.connection
        if not conn:
            conn = await transaction.connection_pool.get_connection()  # pyright: ignore[reportUnknownMemberType]
            conn = cast("Connection", conn)
            transaction.connection = conn

        return await conn.retry.call_with_retry(  # pyright: ignore[reportUnknownVariableType]
            lambda: transaction._execute_transaction(conn, transaction.command_stack, raise_on_error),  # noqa: SLF001 # pyright: ignore[reportUnknownMemberType, reportUnknownLambdaType, reportPrivateUsage]
            lambda error: transaction._disconnect_raise_on_watching(conn, error),  # noqa: SLF001 # pyright: ignore[reportPrivateUsage]
        )

    @staticmethod
    def _process_jsons(
        results: list[Any],
        json_keys: tuple[str, ...],
        json_command_stack: dict[int, CommandT],
    ) -> tuple[list[Any], dict[str, dict[str, Any]]]:
        json_dicts: dict[str, dict[str, Any]] = {}
        for index in range(len(json_keys) - 1, -1, -1):
            key = json_keys[index]
            value = results.pop()
            json_dicts[key] = orjson.loads(value)

        for index, (command, _) in json_command_stack.items():
            cmd = command[0]
            key = str(command[1])
            path = str(command[2])

            match cmd:
                case CommandKind.GET.name:
                    results.insert(index, json_dicts[key][path])
                case CommandKind.SET.name:
                    value = command[3]
                    _ = command[4]
                    expire = command[5]
                    json_dicts[key][path] = value
                    results.insert(index, True)
                case _:  # CommandKind.DEL.name:
                    json_dicts[key][path] = None
                    results.insert(index, 1)

        return results, json_dicts

    @override
    async def execute_transaction(self, transaction: object) -> list[Any]:
        transaction = cast("Pipeline", transaction)

        res = self._json_commands(transaction.command_stack)
        transaction.command_stack, json_keys, need_update_json_keys, json_command_stack = res
        # if there are no JSON keys just executes transaction
        if not json_keys:
            return await transaction.execute()

        # appends GET commands to the command's stack
        for json_key in json_keys:
            transaction.get(json_key)

        if need_update_json_keys:
            results = await self._execute_without_reset(transaction)
            transaction.command_stack = []

            results, json_dicts = self._process_jsons(results, json_keys, json_command_stack)

            for key in need_update_json_keys:
                transaction.set(key, orjson.dumps(json_dicts[key]))
            await transaction.execute()
        else:
            results = await transaction.execute()
            results, _ = self._process_jsons(results, json_keys, json_command_stack)

        return results

    @override
    async def close(self) -> None:
        await self.redis.close()
        logger.info("Disconnected from Redis")

    @override
    def set(self, transaction: object, name: str, path: str, value: str | int, expire: ExpireT) -> bool:
        transaction = cast("Pipeline", transaction)
        if path:
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())
            value = cast("str", value)
            expire_str = cast("str", expire)
            transaction.command_stack.append(((CommandKind.SET.name, name, path, value, "EX", expire_str), {}))
        transaction.set(name, value, ex=expire)
        return cast("bool", None)

    @override
    def get(self, transaction: object, name: str, path: str = "") -> str | None:
        transaction = cast("Pipeline", transaction)
        if path:
            transaction.command_stack.append(((CommandKind.GET.name, name, path), {"keys": [name]}))
        else:
            transaction.get(name)

    @override
    def delete(self, transaction: object, name: str, path: str) -> int:
        transaction = cast("Pipeline", transaction)
        if path:
            transaction.command_stack.append(((CommandKind.DEL.name, name, path), {}))
        else:
            transaction.delete(name)
        return cast("int", None)

    @staticmethod
    def _create_connection_pool() -> ConnectionPool:
        return ConnectionPool.from_url(NOSQL_DB_CFG.url, max_connections=NOSQL_DB_CFG.max_pool_size)  # pyright: ignore[reportUnknownMemberType]
