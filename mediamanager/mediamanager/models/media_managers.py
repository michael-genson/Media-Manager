from abc import abstractproperty

from humps import camelize
from pydantic import BaseModel, Field


class BaseMediaManagerMedia(BaseModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True

    id: str

    title: str
    tag_ids: list[str] | None = Field(None, alias="tags")
    path: str
    root_folder_path: str

    @abstractproperty
    def db_url(self) -> str:
        ...


class RadarrMedia(BaseMediaManagerMedia):
    tmdb_id: str

    @property
    def db_url(self) -> str:
        return f"https://www.themoviedb.org/movie/{self.tmdb_id}"


class SonarrMedia(BaseMediaManagerMedia):
    tvdb_id: str

    @property
    def db_url(self) -> str:
        return f"https://www.thetvdb.com/dereferrer/series/{self.tvdb_id}"


class MediaManagerTag(BaseModel):
    id: str
    label: str
