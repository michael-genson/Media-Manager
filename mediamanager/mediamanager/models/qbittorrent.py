from datetime import datetime
from enum import Enum

from pydantic import Field
from pydantic.dataclasses import dataclass

from ._base import APIBase


class FileSizeUnit(Enum):
    BYTES = "bytes"
    KB = "kb"
    MB = "mb"
    GB = "gb"


class QBTState(Enum):
    ALLOCATING = "allocating"
    CHECKING_DOWNLOAD = "checkingDL"
    CHECKING_RESUME_DATA = "checkingResumeData"
    CHECKING_UPLOAD = "checkingUP"
    DOWNLOADING = "downloading"
    ERROR = "error"
    FORCED_DOWNLOAD = "forcedDL"
    FORCED_UPLOAD = "forcedUP"
    METADATA_DOWNLOAD = "metaDL"
    MISSING_FILES = "missingFiles"
    MOVING = "moving"
    PAUSED_DOWNLOAD = "pausedDL"
    PAUSED_UPLOAD = "pausedUP"
    QUEUED_DOWNLOAD = "queuedDL"
    QUEUED_UPLOAD = "queuedUP"
    STALLED_DOWNLOAD = "stalledDL"
    STALLED_UPLOAD = "stalledUP"
    UNKNOWN = "unknown"
    UPLOADING = "uploading"

    @classmethod
    def _missing_(cls, _):
        return cls.UNKNOWN


@dataclass(frozen=True)
class FileSize:
    bytes: float

    @property
    def kb(self) -> float:
        return self.bytes * 1024

    @property
    def mb(self) -> float:
        return self.kb * 1024

    @property
    def gb(self) -> float:
        return self.mb * 1024

    @property
    def tb(self) -> float:
        return self.gb * 1024

    def _label(self, amount: float, unit: FileSizeUnit, precision: int = 2) -> str:
        amount_label = str(int(amount) if amount.is_integer() else round(amount, precision))
        return f"{amount_label} {unit.value}"

    def bytes_label(self, precision: int = 2) -> str:
        return self._label(self.bytes, FileSizeUnit.BYTES, precision)

    def kb_label(self, precision: int = 2) -> str:
        return self._label(self.kb, FileSizeUnit.KB, precision)

    def mb_label(self, precision: int = 2) -> str:
        return self._label(self.mb, FileSizeUnit.MB, precision)

    def gb_label(self, precision: int = 2) -> str:
        return self._label(self.gb, FileSizeUnit.GB, precision)


@dataclass(frozen=True)
class Percent:
    value: float

    @property
    def percent(self) -> float:
        return self.value * 100

    def label(self, precision: int = 2) -> str:
        val = str(int(self.value) if self.value.is_integer() else round(self.value, precision))
        return f"{val}%"


class QBTTorrent(APIBase):
    _complex_types = [FileSize, Percent]

    hash: str
    """The unique hash of this torrent"""

    added_on: datetime
    amount_left: FileSize | None = None
    last_activity: datetime | None = None
    category: str | None = None

    size: FileSize | None = None
    total_size: FileSize | None = None
    completed: FileSize | None = None
    completed_on: datetime | None = None

    progress: Percent | None = None
    downloaded: FileSize | None = None
    download_speed: FileSize | None = Field(None, alias="dlspeed")
    uploaded: FileSize | None = None
    upload_speed: FileSize | None = Field(None, alias="upspeed")

    state: QBTState

    num_seeds: int | None = None
    num_leechs: int | None = None

    polled_at: datetime = Field(default_factory=datetime.now)
    """When this data was polled. Used for determining if this torrent is stalled"""

    @property
    def id(self) -> str:
        return self.hash

    def is_stalled(self, threshold: int = 3) -> bool:
        """Returns if a torrent is stalled, with an optional threshold in seconds"""

        stalled_for = self.polled_at - (self.last_activity or self.added_on)
        return stalled_for.seconds >= threshold


class QBTTorrentFilter(Enum):
    all = "all"
    downloading = "downloading"
    seeding = "seeding"
    completed = "completed"
    paused = "paused"
    active = "active"
    inactive = "inactive"
    resumed = "resumed"
    stalled = "stalled"
    stalled_uploading = "stalled_uploading"
    stalled_downloading = "stalled_downloading"
    errored = "errored"
