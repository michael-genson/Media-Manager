import pytest

from mediamanager.services.factory import ServiceFactory


@pytest.fixture()
def svcs() -> ServiceFactory:
    return ServiceFactory()
