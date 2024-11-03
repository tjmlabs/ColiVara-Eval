import pytest
from unittest.mock import MagicMock
import pandas as pd
from src.document_manager import check_collection, upsert_documents


@pytest.fixture
def client():
    return MagicMock()


@pytest.fixture
def collection_name():
    return "test_collection"


@pytest.fixture
def df():
    return pd.DataFrame(
        {
            "id": [1, 2],
            "image_base64": ["base64string1", "base64string2"],
            "docId": [101, 102],
            "image_filename": ["image1.png", "image2.png"],
        }
    )


def test_check_collection_exists(client, collection_name):
    mock_collection = MagicMock()
    mock_collection.name = collection_name
    client.list_collections.return_value = [mock_collection]

    result = check_collection(client, collection_name)
    assert result


def test_check_collection_not_exists(client, collection_name):
    client.get_collections.return_value = [{"name": "other_collection"}]
    result = check_collection(client, collection_name)
    assert not result


def test_upsert_documents_creates_collection(client, df, collection_name):
    client.get_collections.return_value = []
    upsert_documents(client, df, collection_name)
    client.create_collection.assert_called_once_with(collection_name)


def test_upsert_documents_upserts_documents(client, df, collection_name):
    client.get_collections.return_value = [{"name": collection_name}]
    upsert_documents(client, df, collection_name)
    assert client.upsert_document.call_count == len(df)


def test_upsert_documents_returns_list(client, df, collection_name):
    client.get_collections.return_value = [{"name": collection_name}]
    client.list_documents.return_value = [{"id": 1}, {"id": 2}]
    result = upsert_documents(client, df, collection_name)
    assert result == [{"id": 1}, {"id": 2}]
