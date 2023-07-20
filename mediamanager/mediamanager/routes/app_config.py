from fastapi import APIRouter, Depends

from .. import security
from ..models.app.config import AppConfig
from ..services.factory import ServiceFactory

router = APIRouter(prefix="/api/config", tags=["App Config"], dependencies=[Depends(security.get_current_user)])


@router.get("", response_model=AppConfig)
def get_app_config() -> AppConfig:
    svcs = ServiceFactory()
    return svcs.app_config.config


@router.put("", response_model=AppConfig)
def update_app_config(new_config: AppConfig) -> AppConfig:
    svcs = ServiceFactory()
    return svcs.app_config.update_config(new_config)
