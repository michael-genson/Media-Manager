import json

from ..db.db_setup import session_context
from ..db.models.app.app_config import AppConfig as AppConfigDB
from ..models.app.app_config import AppConfig
from ..settings import app_settings


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
            defaults = app_settings._AppConfigDefaults()
            default_config = AppConfig(**defaults.dict())
            config = AppConfigDB(**default_config.dict(exclude={"monitored_library_ids"}))

            session.add(config)
            session.commit()
            return AppConfig.from_orm(config)

    def patch_config(self, /, **kwargs) -> AppConfig:
        with session_context() as session:
            config_db = session.query(AppConfigDB).first()
            if not config_db:
                raise Exception("config does not exist")

            # encode monitored_library_ids as a JSON string, or remove it if explicitly passed to kwargs as null/empty
            if "monitored_library_ids" in kwargs:
                monitored_library_ids: list[str] | None = kwargs.pop("monitored_library_ids")
                if not monitored_library_ids:
                    kwargs["monitored_library_ids_json"] = None
                else:
                    kwargs["monitored_library_ids_json"] = json.dumps(monitored_library_ids)

            config_db.update(**kwargs)
            session.commit()

            self._config = AppConfig.from_orm(config_db)
            return self._config

    def update_config(self, config: AppConfig) -> AppConfig:
        return self.patch_config(**config.dict())
