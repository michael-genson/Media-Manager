from abc import abstractproperty

from humps import camelize
from pydantic import BaseModel, Field


class BaseMediaManagerMedia(BaseModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True

    id: str
    db_id: str

    title: str
    tag_ids: list[str] | None = Field(None, alias="tags")
    path: str
    root_folder_path: str

    @abstractproperty
    def db_url(self) -> str:
        ...


class RadarrMedia(BaseMediaManagerMedia):
    db_id: str = Field(..., alias="tmdbId")

    @property
    def db_url(self) -> str:
        return f"https://www.themoviedb.org/movie/{self.db_id}"


class SonarrMedia(BaseMediaManagerMedia):
    db_id: str = Field(..., alias="tvdbId")

    @property
    def db_url(self) -> str:
        return f"https://www.thetvdb.com/dereferrer/series/{self.db_id}"


class MediaManagerTag(BaseModel):
    id: str
    label: str
