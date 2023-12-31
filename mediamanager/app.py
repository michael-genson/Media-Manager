from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .settings import app_settings, scheduler_settings

### App Setup ###
APP_DIR = app_settings.APP_DIR
CONFIG_DIR = app_settings.CONFIG_DIR
STATIC_DIR = app_settings.STATIC_DIR

schedules = scheduler_settings.SchedulerSettings()
settings = app_settings.AppSettings()

secrets = app_settings.AppSecrets()
secrets.db_secret_key  # force generation of secret key on a new instance


expired_media_settings = app_settings.ExpiredMediaSettings()

app = FastAPI(title=settings.app_title, version=settings.app_version)
app.mount("/static", StaticFiles(directory=app_settings.STATIC_DIR), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


### Route Setup ###
from .routes import app_config, auth, expired_media, manage_media, users  # noqa: E402

# Mypy bugs out when determining the router types, so we ignore the type errors
app.include_router(app_config.router)  # type: ignore
app.include_router(auth.router)  # type: ignore
app.include_router(expired_media.router)  # type: ignore
app.include_router(manage_media.router)  # type: ignore
app.include_router(users.router)  # type: ignore
app.include_router(users.default_user_router)  # type: ignore


# default route
@app.get("/", response_class=RedirectResponse, include_in_schema=False)
def home():
    if app.docs_url:
        return RedirectResponse(app.docs_url, status_code=status.HTTP_302_FOUND)
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
