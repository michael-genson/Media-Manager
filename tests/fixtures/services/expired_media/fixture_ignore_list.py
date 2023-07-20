import os
import shutil
from tempfile import NamedTemporaryFile

import pytest

from mediamanager.mediamanager.app import STATIC_DIR, expired_media_settings
from mediamanager.mediamanager.models.expired_media.ignored_items import (
    ExpiredMediaIgnoredItemIn,
    ExpiredMediaIgnoredItems,
)
from mediamanager.mediamanager.services.expired_media import ExpiredMediaIgnoreListManager
from tests.utils.generators import random_string


@pytest.fixture
def expired_media_ignore_list_manager() -> ExpiredMediaIgnoreListManager:
    return ExpiredMediaIgnoreListManager()


@pytest.fixture
async def expired_media_ignored_items(
    expired_media_ignore_list_manager: ExpiredMediaIgnoreListManager,
) -> ExpiredMediaIgnoredItems:
    return await expired_media_ignore_list_manager.add(
        [ExpiredMediaIgnoredItemIn(rating_key=random_string(), name=random_string()) for _ in range(10)]
    )


### Setup and Teardown ###


def _reset_file() -> None:
    lm = ExpiredMediaIgnoreListManager()
    shutil.copyfile(
        f"{STATIC_DIR}/default_configs/{os.path.basename(expired_media_settings.expired_media_ignore_file)}", lm.fp
    )


@pytest.fixture(scope="session", autouse=True)
def mock_ignore_list():
    fp = NamedTemporaryFile(delete=False, suffix="json").name
    mp = pytest.MonkeyPatch()
    mp.setattr(ExpiredMediaIgnoreListManager, "fp", fp)

    _reset_file()
    yield
    os.unlink(fp)


@pytest.fixture(autouse=True)
def reset():
    yield
    _reset_file()
