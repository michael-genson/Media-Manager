from ..app import secrets, settings
from ..db.db_setup import session_context
from ..db.models.app.app_config import AppConfig as AppConfigDB
from ..models.app.config import AppConfig


class AppConfigService:
    def __init__(self) -> None:
        self._config: AppConfig | None = None

    @property
    def config(self):
        if not self._config:
            with session_context() as session:
                config = session.query(AppConfigDB).first()
                self._config = AppConfig.from_orm(config) if config else self._create_new_config()

        return self._config

    def _create_new_config(self) -> AppConfig:
        with session_context() as session:
            # create default config from environment vars
            default_config = AppConfig(**settings.dict(), **secrets.dict())
            config = AppConfigDB(**default_config.dict())

            session.add(config)
            session.commit()
            return AppConfig.from_orm(config)

    def patch_config(self, /, **kwargs) -> AppConfig:
        with session_context() as session:
            config_db = session.query(AppConfigDB).first()
            if not config_db:
                raise Exception("config does not exist")

            config_db.update(**kwargs)
            session.commit()

            self._config = AppConfig.from_orm(config_db)
            return self._config

    def update_config(self, config: AppConfig) -> AppConfig:
        return self.patch_config(**config.dict())
