from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .settings import _app_settings, scheduler_settings

### App Setup ###
APP_DIR = _app_settings.APP_DIR
CONFIG_DIR = _app_settings.CONFIG_DIR
STATIC_DIR = _app_settings.STATIC_DIR

schedules = scheduler_settings.SchedulerSettings()
secrets = _app_settings.AppSecrets()
settings = _app_settings.AppSettings()


expired_media_settings = _app_settings.ExpiredMediaSettings()

app = FastAPI(title=settings.app_title, version=settings.app_version)
app.mount("/static", StaticFiles(directory=_app_settings.STATIC_DIR), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
