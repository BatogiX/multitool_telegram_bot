from abc import ABC

from models.kv import BaseKeyValue, BaseKeyValueSet, BaseKeyValueGet


class BaseCacheUserCreated(BaseKeyValue, ABC):
    @property
    def key(self) -> str:
        return self.key_builder.build(self.storage_key, "user_created")


class SetCacheUserCreated(BaseKeyValueSet, BaseCacheUserCreated): ...
class GetCacheUserCreated(BaseKeyValueGet, BaseCacheUserCreated): ...
