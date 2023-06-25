from datetime import UTC, datetime
from enum import Enum
from typing import TypeVar

from pydantic import BaseModel, validator

T = TypeVar("T")


class OrderDirection(Enum):
    ascending = "asc"
    descending = "desc"


class LibraryType(Enum):
    movie = "movie"
    show = "show"
    unknown = "unknown"
    """Default unsupported value"""

    @classmethod
    def _missing_(cls, value: object):
        return cls.unknown


class TautulliLibrary(BaseModel):
    section_id: str
    """The unique id of the library"""

    section_name: str
    """The display name of the library"""
    section_type: LibraryType
    count: int
    """
    The number of direct children in the library

    e.g. the number of seasons in a show (not the number of episodes)
    """
    is_active: bool


class TautulliMediaSummary(BaseModel):
    section_id: str
    """The unique id of the parent library"""
    rating_key: str
    """The unique id of the media"""

    media_type: LibraryType
    title: str

    added_at: datetime
    last_played: datetime | None = None

    @validator("added_at", "last_played")
    def validate_timezone(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return v

        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            v = v.replace(tzinfo=UTC)

        return v


class TautulliMediaDetail(BaseModel):
    section_id: str
    """The unique id of the parent library"""
    rating_key: str
    """The unique id of the media"""

    media_type: LibraryType
    title: str
    guids: list[str] | None = None

    def get_guid(self, prefix: str) -> str | None:
        if not self.guids:
            return None

        prefix = prefix.lower()
        for guid in self.guids:
            try:
                guid_prefix, guid_value = guid.split("://", 1)
                if prefix == guid_prefix.lower():
                    return guid_value
            except ValueError:
                continue

        return None


class TautulliMedia(BaseModel):
    library: TautulliLibrary
    media_summary: TautulliMediaSummary
    media_detail: TautulliMediaDetail


class TautulliFailedDeletedMedia(BaseModel):
    """Map of rating key to detail, when available"""

    failed_items: dict[str, TautulliMediaDetail | None]
