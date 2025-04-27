from models.kv.base import BaseKeyValueGet, BaseKeyValue, BaseKeyValueSet


class BaseCacheUserCreated(BaseKeyValue):
    @property
    def key(self) -> str:
        return self.key_builder.build(self.storage_key, "user_created")


class SetCacheUserCreated(BaseKeyValueSet, BaseCacheUserCreated): ...


class GetCacheUserCreated(BaseKeyValueGet, BaseCacheUserCreated): ...
