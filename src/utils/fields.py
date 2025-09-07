from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING, Any, cast

from pydantic import BaseModel

if TYPE_CHECKING:
    from sqlalchemy.orm import InstrumentedAttribute


@dataclass(frozen=True)
class _GetFields:
    _model: type[BaseModel]

    def __getattr__(self, item: str) -> str:
        if item in self._model.model_fields:
            return item

        return getattr(self._model, item)


def fields[TModel: type[BaseModel]](model: TModel, /) -> TModel:
    return cast("TModel", _GetFields(model))


if not TYPE_CHECKING:
    fields = lru_cache(maxsize=256)(fields)


def key_of(field: object) -> str:
    field = cast("InstrumentedAttribute[Any]", field)
    return field.key
