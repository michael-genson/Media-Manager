from typing import Generic, TypeVar

from humps.main import camelize

from .._base import BaseModelMM


class APIBase(BaseModelMM):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


T = TypeVar("T", bound=APIBase)


class GenericCollection(APIBase, Generic[T]):
    items: list[T]
