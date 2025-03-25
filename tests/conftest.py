import pytest

from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import create_app

@pytest.fixture(scope="session")
def app():
    return create_app(api_env='TEST')

@pytest.fixture(scope="session")
def client(app):
    return TestClient(app=app)
