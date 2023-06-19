import os
import pathlib

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .settings import app_settings, scheduler_settings

### App Setup ###
current_dir = str(pathlib.Path(__file__).parent.resolve())

schedules = scheduler_settings.SchedulerSettings()
secrets = app_settings.AppSecrets()
settings = app_settings.AppSettings()

expired_media_settings = app_settings.ExpiredMediaSettings()

app = FastAPI(title=settings.app_title, version=settings.app_version)
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")


### Route Setup ###
from .routes import expired_media  # noqa: E402

# Mypy bugs out when determining the router types, so we ignore the type errors
app.include_router(expired_media.router)  # type: ignore


# default route
@app.get("/", response_class=RedirectResponse, include_in_schema=False)
def home():
    if app.docs_url:
        return RedirectResponse(app.docs_url, status_code=status.HTTP_302_FOUND)
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
