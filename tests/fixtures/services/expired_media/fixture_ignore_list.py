import pytest

from mediamanager.models.expired_media.ignored_items import ExpiredMediaIgnoredItem, ExpiredMediaIgnoredItemIn
from mediamanager.services.expired_media import ExpiredMediaIgnoreListManager
from tests.utils.generators import random_string


@pytest.fixture
def expired_media_ignore_list_manager() -> ExpiredMediaIgnoreListManager:
    return ExpiredMediaIgnoreListManager()


@pytest.fixture
async def expired_media_ignored_items(
    expired_media_ignore_list_manager: ExpiredMediaIgnoreListManager,
) -> list[ExpiredMediaIgnoredItem]:
    await expired_media_ignore_list_manager.add(
        [ExpiredMediaIgnoredItemIn(rating_key=random_string(), name=random_string()) for _ in range(10)]
    )

    return expired_media_ignore_list_manager.get_all()
