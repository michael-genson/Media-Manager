#!/usr/bin/python

import asyncio
import os
import shutil
from types import FrameType

import uvicorn

from mediamanager.app import CONFIG_DIR, STATIC_DIR, app, expired_media_settings, settings  # type: ignore
from mediamanager.db.db_setup import init_db  # type: ignore
from mediamanager.scheduler import scheduler  # type: ignore


class Server(uvicorn.Server):
    """Custom Uvicorn server to shut down Rocketry"""

    def handle_exit(self, sig: int, frame: FrameType | None) -> None:
        scheduler.session.shut_down()
        return super().handle_exit(sig, frame)


def _create_missing_json_files():
    files = [expired_media_settings.expired_media_ignore_file]

    for file in files:
        fp = os.path.join(CONFIG_DIR, file)
        if not os.path.exists(fp):
            shutil.copyfile(f"{STATIC_DIR}/default_configs/{os.path.basename(fp)}", fp)


def setup():
    """Run server setup tasks"""

    _create_missing_json_files()
    init_db()


async def main():
    setup()

    server = Server(
        config=uvicorn.Config(
            app,
            workers=settings.uvicorn_workers,
            loop="asyncio",
            host="0.0.0.0",
            port=int(os.environ.get("APP_PORT", 9000)),
        )
    )

    api = asyncio.create_task(server.serve())
    sched = asyncio.create_task(scheduler.serve())

    await asyncio.wait([sched, api])


if __name__ == "__main__":
    asyncio.run(main())
