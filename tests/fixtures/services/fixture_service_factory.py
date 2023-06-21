import pytest

from mediamanager.mediamanager.services.factory import ServiceFactory


@pytest.fixture()
def svcs() -> ServiceFactory:
    return ServiceFactory()
