import asyncio
import time

from sqlalchemy import update

from ..db.db_setup import session_context
from ..db.models.expired_media.ignored_items import ExpiredMediaIgnoredItem as ExpiredMediaIgnoredItemDB
from ..models.expired_media.ignored_items import (
    ExpiredMediaIgnoredItem,
    ExpiredMediaIgnoredItemIn,
    ExpiredMediaIgnoredItems,
)
from .factory import ServiceFactory


class ExpiredMediaIgnoreListManager:
    # TODO: optimize this to not constantly read all items (query for specific items instead, like a normal db service)

    @classmethod
    def _check_if_expired(cls, item: ExpiredMediaIgnoredItemDB) -> bool:
        return time.time() >= item.ttl if item.ttl is not None else False

    def get_all(self) -> ExpiredMediaIgnoredItems:
        with session_context() as session:
            live_items: list[ExpiredMediaIgnoredItemDB] = []
            for item in session.query(ExpiredMediaIgnoredItemDB).all():
                if not self._check_if_expired(item):
                    live_items.append(item)
                else:
                    session.delete(item)

            session.commit()
            return ExpiredMediaIgnoredItems(items=[ExpiredMediaIgnoredItem.from_orm(item) for item in live_items])

    async def _process_expired_media_ignored_item(
        self, svcs: ServiceFactory, media: ExpiredMediaIgnoredItemIn
    ) -> ExpiredMediaIgnoredItemIn:
        if media.name:
            return media

        detail = await svcs.tautulli.get_media_detail(media.rating_key)
        media.name = detail.title
        return media

    async def add(self, media: list[ExpiredMediaIgnoredItemIn]) -> list[ExpiredMediaIgnoredItem]:
        svcs = ServiceFactory()
        items_to_add_futures = [self._process_expired_media_ignored_item(svcs, new_media) for new_media in media]
        new_ignored_items: list[ExpiredMediaIgnoredItemIn] = await asyncio.gather(*items_to_add_futures)

        with session_context() as session:
            # if an ignored item's rating key is already saved, we need to update those instead of adding duplicates
            new_items_by_rating_key = {item.rating_key: item for item in new_ignored_items}
            queried_items = (
                session.query(ExpiredMediaIgnoredItemDB)
                .filter(ExpiredMediaIgnoredItemDB.rating_key.in_(new_items_by_rating_key.keys()))
                .all()
            )

            # generate update data by combining new data and the existing data's id
            update_data = [
                new_items_by_rating_key.pop(queried_item.rating_key).dict() | {"id": queried_item.id}
                for queried_item in queried_items
            ]

            session.execute(update(ExpiredMediaIgnoredItemDB), update_data)

            # since we pop off the existing data, the remaining values are new items
            items = [ExpiredMediaIgnoredItemDB(**new_item.dict()) for new_item in new_items_by_rating_key.values()]
            session.add_all(items)
            session.commit()

            items_out: list[ExpiredMediaIgnoredItem] = []
            for item in items:
                session.refresh(item)
                items_out.append(ExpiredMediaIgnoredItem.from_orm(item))

            return items_out

    def delete(self, rating_keys: list[str]) -> list[ExpiredMediaIgnoredItem]:
        with session_context() as session:
            items_to_delete = (
                session.query(ExpiredMediaIgnoredItemDB)
                .filter(ExpiredMediaIgnoredItemDB.rating_key.in_(rating_keys))
                .all()
            )

            deleted_items = [ExpiredMediaIgnoredItem.from_orm(item) for item in items_to_delete]
            for item in items_to_delete:
                session.delete(item)

            session.commit()
            return deleted_items
