from typing import TypeVar

from humps.main import camelize
from pydantic import BaseModel, root_validator
from pydantic.fields import ModelField

T = TypeVar("T", bound=BaseModel)


class BaseModelMM(BaseModel):
    _complex_types: list[type] | None = None
    """
    List of complex types to convert values into during construction (e.g. a `float` into a `Percent`)

    Complex types must accept a single argument (e.g. `Percent(0.05)`)
    """

    @classmethod
    def _get_class_fields(cls, include_aliases: bool = False) -> dict[str, ModelField]:
        """
        Returns a dictionary of fieldnames and field definitions,
        optionally including field aliases as separate keys
        """

        fields = cls.__fields__
        if not include_aliases:
            return fields
        else:
            return fields | {field.alias: field for field in fields.values() if field.has_alias}

    @root_validator(pre=True)
    def _convert_values_into_complex_types(cls, values: dict) -> dict:
        if not cls._complex_types:
            return values

        for fieldname, value in values.items():
            if fieldname not in (class_fields := cls._get_class_fields(True)):
                continue
            for complex_type in cls._complex_types:
                if class_fields[fieldname].type_ != complex_type:
                    continue
                values[fieldname] = complex_type(value)

        return values

    def cast(self, cls: type[T], **kwargs) -> T:
        """
        Cast the current model to another with additional arguments. Useful for
        transforming DTOs into models that are saved to a database
        """
        create_data = {field: getattr(self, field) for field in self.__fields__ if field in cls.__fields__}
        create_data.update(kwargs or {})
        return cls(**create_data)

    def map_to(self, dest: T) -> T:
        """
        Map matching values from the current model to another model. Model returned
        for method chaining.
        """

        for field in self.__fields__:
            if field in dest.__fields__:
                setattr(dest, field, getattr(self, field))

        return dest

    def map_from(self, src: BaseModel):
        """
        Map matching values from another model to the current model.
        """

        for field in src.__fields__:
            if field in self.__fields__:
                setattr(self, field, getattr(src, field))

    def merge(self, src: T, replace_null=False):
        """
        Replace matching values from another instance to the current instance.
        """

        for field in src.__fields__:
            val = getattr(src, field)
            if field in self.__fields__ and (val is not None or replace_null):
                setattr(self, field, val)


class APIBase(BaseModelMM):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True
