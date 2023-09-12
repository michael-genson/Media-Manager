from typing import Generic, TypeVar

from humps.main import camelize
from pydantic.generics import GenericModel

from .._base import BaseModelMM


class APIBase(BaseModelMM):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


T = TypeVar("T", bound=APIBase)


class GenericCollection(GenericModel, Generic[T]):
    items: list[T]
