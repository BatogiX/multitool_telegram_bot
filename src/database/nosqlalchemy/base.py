from typing import Any, final


@final
class SimpleField:
    def __init__(self, key: str, type_hint: type) -> None:
        self.key = key
        self.type = type_hint

    def __repr__(self) -> str:
        type_name = getattr(self.type, "__name__", repr(self.type))
        return f"<SimpleField {self.key}: {type_name}>"


@final
class JsonField:
    def __init__(self, key: str, type_hint: type, *, suffix: str) -> None:
        self.key = key
        self.type = type_hint
        self.suffix = suffix.lower()

    def __repr__(self) -> str:
        type_name = getattr(self.type, "__name__", repr(self.type))
        return f"<JsonField {self.key}: {type_name}>"


@final
class SchemaMeta(type):
    def __new__(cls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> type:
        annotations = namespace.get("__annotations__", {})
        for key, type_hint in annotations.items():
            namespace[key] = SimpleField(key, type_hint)
        return super().__new__(cls, name, bases, namespace)


@final
class JsonSchemaMeta(type):
    def __new__(cls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> type:
        annotations = namespace.get("__annotations__", {})
        for key, type_hint in annotations.items():
            namespace[key] = JsonField(key, type_hint, suffix=name)
        return super().__new__(cls, name, bases, namespace)


class BaseSchema:
    def __init_subclass__(cls) -> None:
        cls._suffix = cls.__name__.lower()


class Schema(BaseSchema, metaclass=SchemaMeta):
    pass


class JsonSchema(BaseSchema, metaclass=JsonSchemaMeta):
    pass
