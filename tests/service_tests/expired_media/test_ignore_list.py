import random
import time

from mediamanager.models.expired_media.ignored_items import (
    ExpiredMediaIgnoredItemIn,
    ExpiredMediaIgnoredItems,
)
from mediamanager.services.expired_media import ExpiredMediaIgnoreListManager
from tests.utils.generators import random_int, random_string


async def test_get_ignore_list(
    expired_media_ignore_list_manager: ExpiredMediaIgnoreListManager,
    expired_media_ignored_items: ExpiredMediaIgnoredItems,
):
    assert expired_media_ignore_list_manager.get_all() == expired_media_ignored_items


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

    updated_items_by_rating_key = {item.rating_key: item for item in expired_media_ignore_list_manager.get_all().items}
    assert len(updated_items_by_rating_key) == len(new_items) + len(expired_media_ignored_items.items)
    for item in new_items + expired_media_ignored_items.items:
        updated_item = updated_items_by_rating_key[item.rating_key]
        updated_item_data = updated_item.dict()
        for k, v in item.dict().items():
            if k == "id":
                continue
            assert v == updated_item_data[k]


async def test_add_duplicate_media(
    expired_media_ignore_list_manager: ExpiredMediaIgnoreListManager,
    expired_media_ignored_items: ExpiredMediaIgnoredItems,
):
    original_items = expired_media_ignore_list_manager.get_all().items

    new_name = random_string()
    item_to_duplicate = random.choice(expired_media_ignored_items.items)
    item_to_duplicate.name = new_name
    await expired_media_ignore_list_manager.add([item_to_duplicate.cast(ExpiredMediaIgnoredItemIn)])

    # the number of items should not change
    updated_items = expired_media_ignore_list_manager.get_all().items
    assert len(updated_items) == len(original_items)

    found = False
    original_items_by_id = {item.id: item for item in original_items}
    for item in updated_items:
        assert item.id in original_items_by_id

        original_item = original_items_by_id[item.id]
        if item.id != item_to_duplicate.id:
            assert item == original_item
        else:
            # the duplicated item should replace the existing item, but keep the original id
            found = True
            assert item.name == new_name

    assert found


async def test_delete_ignored_media(
    expired_media_ignore_list_manager: ExpiredMediaIgnoreListManager,
    expired_media_ignored_items: ExpiredMediaIgnoredItems,
):
    rating_keys_to_delete = [
        item.rating_key for item in random.sample(expired_media_ignored_items.items, random_int(1, 5))
    ]
    expired_media_ignore_list_manager.delete(rating_keys_to_delete)

    updated_items = expired_media_ignore_list_manager.get_all()
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
    updated_items = expired_media_ignore_list_manager.get_all()

    expired_rating_keys = [item.rating_key for item in items_to_expire]
    assert updated_items.items == [
        item for item in expired_media_ignored_items.items if item.rating_key not in expired_rating_keys
    ]
