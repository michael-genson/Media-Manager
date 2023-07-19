import asyncio
import json
import os

from ..app import CONFIG_DIR, expired_media_settings
from ..models.expired_media import ExpiredMediaIgnoredItem, ExpiredMediaIgnoredItemIn, ExpiredMediaIgnoredItems
from .factory import ServiceFactory


class ExpiredMediaIgnoreListManager:  # TODO: this should be in the database instead of a JSON file
    def __init__(self) -> None:
        self._fp: str | None = None

    @property
    def fp(self) -> str:
        if self._fp is None:
            self._fp = os.path.join(CONFIG_DIR, expired_media_settings.expired_media_ignore_file)

        return self._fp

    async def _save(self, ignored_items: ExpiredMediaIgnoredItems) -> None:
        with open(self.fp, "w") as f:
            json.dump(ignored_items.dict(), f, indent=2)

    async def _load(self, save_after_pruning: bool = True) -> ExpiredMediaIgnoredItems:
        """
        Load ignore list config file, removing any expired ignore list items

        Optionally save the config file after pruning expired items (default)
        """
        ignored_items = ExpiredMediaIgnoredItems.parse_file(self.fp)

        # remove expired ignore items
        reduced_ignored_items = [item for item in ignored_items.items if not item.is_expired]
        if len(ignored_items.items) != len(reduced_ignored_items):
            ignored_items.items = reduced_ignored_items
            if save_after_pruning:
                await self._save(ignored_items)

        return ignored_items

    async def load(self) -> ExpiredMediaIgnoredItems:
        return await self._load()

    async def _process_expired_media_ignored_item(
        self, svcs: ServiceFactory, media: ExpiredMediaIgnoredItemIn
    ) -> ExpiredMediaIgnoredItem:
        if media.name:
            return media.cast(ExpiredMediaIgnoredItem)

        detail = await svcs.tautulli.get_media_detail(media.rating_key)
        return media.cast(ExpiredMediaIgnoredItem, name=detail.title)

    async def add(self, media: list[ExpiredMediaIgnoredItemIn]) -> ExpiredMediaIgnoredItems:
        ignored_items = await self._load(save_after_pruning=False)

        # remove items that are going to be added to avoid duplicates
        rating_keys_to_add = set(item.rating_key for item in media)
        ignored_items.items[:] = [item for item in ignored_items.items if item.rating_key not in rating_keys_to_add]

        # process items and add them to the items list
        svcs = ServiceFactory()
        items_to_add_futures = [self._process_expired_media_ignored_item(svcs, new_media) for new_media in media]
        ignored_items.items.extend(await asyncio.gather(*items_to_add_futures))

        await self._save(ignored_items)
        return ignored_items

    async def delete(self, rating_keys: list[str]) -> ExpiredMediaIgnoredItems:
        ignored_items = await self._load(save_after_pruning=False)
        ignored_items.items[:] = [item for item in ignored_items.items if item.rating_key not in rating_keys]

        await self._save(ignored_items)
        return ignored_items
