from ..app import secrets, settings
from ..db.db_setup import session_context
from ..db.models.app.config import AppConfig as AppConfigDB
from ..models.app.config import AppConfig


class AppConfigService:
    def __init__(self) -> None:
        self._config: AppConfig | None = None

    @property
    def config(self):
        if not self._config:
            with session_context() as session:
                config = session.query(AppConfigDB).first()
                if not config:
                    # create default config from environment vars
                    default_config = AppConfig(**settings.dict(), **secrets.dict())
                    config = AppConfigDB(**default_config.dict())

                    session.add(config)
                    session.commit()

                self._config = AppConfig.from_orm(config)

        return self._config
