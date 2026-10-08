import pytest
from fastapi.testclient import TestClient

from auth_service.config import Settings
from auth_service.main import create_app


@pytest.fixture
def settings(tmp_path):
    return Settings(
        database_path=tmp_path / "test.db",
        jwt_secret_key="test-secret-key-that-is-at-least-32-characters",
    )


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as test_client:
        yield test_client