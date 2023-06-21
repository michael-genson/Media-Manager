from tests.utils.generators import random_datetime, random_int, random_string
from .mock_tautulli_database import TautulliMockDatabase
from mediamanager.mediamanager.clients.tautulli import TautulliClient
from mediamanager.mediamanager.models.tautulli import (
    TautulliLibrary,
    LibraryType,
    TautulliMedia,
    TautulliMediaDetail,
    TautulliMediaSummary,
)
import pytest

_mock_tautulli_db = TautulliMockDatabase()


@pytest.fixture
def tautulli_libraries() -> dict[LibraryType, TautulliLibrary]:
    libraries: dict[LibraryType, TautulliLibrary] = {}
    for library_type in [LibraryType.movie, LibraryType.show]:
        library = TautulliLibrary(
            section_id=random_string(), section_name=random_string(), section_type=library_type, count=0, is_active=True
        )

        _mock_tautulli_db._insert(_mock_tautulli_db.LIBRARIES, library.section_id, library.dict())
        libraries[library_type] = library

    return libraries


def _populate_media(libraries: dict[LibraryType, TautulliLibrary], library_type: LibraryType) -> list[TautulliMedia]:
    library = libraries[library_type]
    library.count += 10
    _mock_tautulli_db._insert(_mock_tautulli_db.LIBRARIES, library.section_id, library.dict())

    media: list[TautulliMedia] = []
    for _ in range(10):
        summary = TautulliMediaSummary(
            section_id=library.section_id,
            rating_key=random_string(),
            media_type=library_type,
            title=random_string(),
            added_at=random_datetime(),
            last_played=random_datetime(),
        )

        detail = TautulliMediaDetail(
            section_id=library.section_id,
            rating_key=summary.rating_key,
            title=summary.title,
            guids=[f"tmdb://{random_int(1000, 10000)}", f"tvdb://{random_int(1000, 10000)}"],
        )

        _mock_tautulli_db._insert(_mock_tautulli_db.SUMMARIES, summary.rating_key, summary.dict())
        _mock_tautulli_db._insert(_mock_tautulli_db.DETAILS, detail.rating_key, detail.dict())
        media.append(TautulliMedia(library=library, media_summary=summary, media_detail=detail))

    return media


@pytest.fixture
def tautulli_movies(tautulli_libraries: dict[LibraryType, TautulliLibrary]) -> list[TautulliMedia]:
    return _populate_media(tautulli_libraries, LibraryType.movie)


@pytest.fixture
def tautulli_shows(tautulli_libraries: dict[LibraryType, TautulliLibrary]) -> list[TautulliMedia]:
    return _populate_media(tautulli_libraries, LibraryType.show)


### Setup and Teardown ###


@pytest.fixture(scope="session", autouse=True)
def mock_tautulli_database():
    mp = pytest.MonkeyPatch()
    mp.setattr(TautulliClient, "client", _mock_tautulli_db)
    yield


@pytest.fixture(autouse=True)
def clean_up_database():
    yield
    _mock_tautulli_db.db.clear()
