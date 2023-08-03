#!/usr/bin/python

import asyncio
import os
from types import FrameType

import uvicorn

from mediamanager.app import app
from mediamanager.db.db_setup import init_db
from mediamanager.scheduler import scheduler
from mediamanager.settings import app_settings

settings = app_settings.AppSettings()


class Server(uvicorn.Server):
    """Custom Uvicorn server to shut down Rocketry"""

    def handle_exit(self, sig: int, frame: FrameType | None) -> None:
        scheduler.session.shut_down()
        return super().handle_exit(sig, frame)


def setup():
    """Run server setup tasks"""

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
