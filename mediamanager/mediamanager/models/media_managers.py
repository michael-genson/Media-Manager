from abc import abstractproperty

from pydantic import Field

from ._base import APIBase


class BaseMediaManagerMedia(APIBase):
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


class MediaManagerTag(APIBase):
    id: str
    label: str
