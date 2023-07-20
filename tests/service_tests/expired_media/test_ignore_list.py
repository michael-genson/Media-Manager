import random
import time

from mediamanager.mediamanager.models.expired_media.ignored_items import (
    ExpiredMediaIgnoredItem,
    ExpiredMediaIgnoredItemIn,
    ExpiredMediaIgnoredItems,
)
from mediamanager.mediamanager.services.expired_media import ExpiredMediaIgnoreListManager
from tests.utils.generators import random_int, random_string


async def test_get_ignore_list(
    expired_media_ignore_list_manager: ExpiredMediaIgnoreListManager,
    expired_media_ignored_items: ExpiredMediaIgnoredItems,
):
    assert await expired_media_ignore_list_manager.load() == expired_media_ignored_items


async def test_add_ignored_media(
    expired_media_ignore_list_manager: ExpiredMediaIgnoreListManager,
    expired_media_ignored_items: ExpiredMediaIgnoredItems,
):
    new_items = [
        ExpiredMediaIgnoredItemIn(
            rating_key=random_string(), name=random_string(), ttl=int(time.time()) + random_int(1000, 10000)
        )
        for _ in range(random_int(1, 10))
    ]
    await expired_media_ignore_list_manager.add(new_items)

    updated_items = await expired_media_ignore_list_manager.load()
    assert updated_items.items == expired_media_ignored_items.items + [
        new_item.cast(ExpiredMediaIgnoredItem) for new_item in new_items
    ]


async def test_delete_ignored_media(
    expired_media_ignore_list_manager: ExpiredMediaIgnoreListManager,
    expired_media_ignored_items: ExpiredMediaIgnoredItems,
):
    rating_keys_to_delete = [
        item.rating_key for item in random.sample(expired_media_ignored_items.items, random_int(1, 5))
    ]
    await expired_media_ignore_list_manager.delete(rating_keys_to_delete)

    updated_items = await expired_media_ignore_list_manager.load()
    assert updated_items.items == [
        item for item in expired_media_ignored_items.items if item.rating_key not in rating_keys_to_delete
    ]


async def test_get_ignore_list_expired_items(
    expired_media_ignore_list_manager: ExpiredMediaIgnoreListManager,
    expired_media_ignored_items: ExpiredMediaIgnoredItems,
):
    items_to_expire = random.sample(expired_media_ignored_items.items, random_int(1, 5))
    for item in items_to_expire:
        item.ttl = int(time.time()) - random_int(100, 1000)

    await expired_media_ignore_list_manager.add([item.cast(ExpiredMediaIgnoredItemIn) for item in items_to_expire])
    updated_items = await expired_media_ignore_list_manager.load()

    expired_rating_keys = [item.rating_key for item in items_to_expire]
    assert updated_items.items == [
        item for item in expired_media_ignored_items.items if item.rating_key not in expired_rating_keys
    ]
