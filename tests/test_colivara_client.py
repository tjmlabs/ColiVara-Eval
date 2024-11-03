import pytest
from src.client import get_colivara_client
from src.config import API_KEY, BASE_URL


@pytest.fixture
def client():
    return get_colivara_client()


def test_client_base_url(client):
    assert client.base_url == BASE_URL


def test_client_api_key(client):
    assert client.api_key == API_KEY


def test_client_initialization(client):
    assert client is not None
    assert hasattr(client, "base_url")
    assert hasattr(client, "api_key")
