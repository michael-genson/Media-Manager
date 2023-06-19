from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from .app import secrets

API_KEY_HEADER_NAME = "X-Api-Key"


def require_api_key(api_key: str = Depends(APIKeyHeader(name=API_KEY_HEADER_NAME))):
    if api_key != secrets.app_api_key:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid API key")
