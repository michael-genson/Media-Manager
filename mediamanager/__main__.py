#!/usr/bin/python

import asyncio
import os
import pathlib
import shutil
from types import FrameType

import uvicorn

from mediamanager.app import app, expired_media_settings, settings  # type: ignore
from mediamanager.scheduler import scheduler  # type: ignore


class Server(uvicorn.Server):
    """Custom Uvicorn server to shut down Rocketry"""

    def handle_exit(self, sig: int, frame: FrameType | None) -> None:
        scheduler.session.shut_down()
        return super().handle_exit(sig, frame)


def create_missing_json_files():
    filepaths = [expired_media_settings.expired_media_ignore_filepath]

    current_dir = str(pathlib.Path(__file__).parent.resolve())
    for fp in filepaths:
        if not os.path.exists(fp):
            shutil.copyfile(f"{current_dir}/mediamanager/static/default_configs/{os.path.basename(fp)}", fp)


async def main():
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

    create_missing_json_files()

    await asyncio.wait([sched, api])


if __name__ == "__main__":
    asyncio.run(main())
