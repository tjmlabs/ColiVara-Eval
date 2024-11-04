import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from src.document_manager import check_collection, upsert_documents
from tqdm import tqdm


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
            "doc_id": [101, 102],
            "image_filename": ["image1.png", "image2.png"],
        }
    )


def test_check_collection_exists(client, collection_name):
    mock_collection = MagicMock()
    mock_collection.name = collection_name
    client.list_collections.return_value = [mock_collection]

    result = check_collection(client, collection_name)
    assert result
    client.list_collections.assert_called_once()


def test_check_collection_not_exists(client, collection_name):
    client.list_collections.return_value = []

    result = check_collection(client, collection_name)
    assert not result
    client.list_collections.assert_called_once()


def test_upsert_documents_creates_collection_if_not_exists(client, df, collection_name):
    client.list_collections.return_value = []

    with patch.object(client, "create_collection") as mock_create_collection:
        upsert_documents(client, df, collection_name)
        mock_create_collection.assert_called_once_with(collection_name)


def test_upsert_documents_skips_create_if_collection_exists(
    client, df, collection_name
):
    mock_collection = MagicMock()
    mock_collection.name = collection_name
    client.list_collections.return_value = [mock_collection]

    with patch.object(client, "create_collection") as mock_create_collection:
        upsert_documents(client, df, collection_name)
        mock_create_collection.assert_not_called()


def test_upsert_documents_upserts_all_documents(client, df, collection_name):
    mock_collection = MagicMock()
    mock_collection.name = collection_name
    client.list_collections.return_value = [mock_collection]

    with patch.object(client, "upsert_document") as mock_upsert_document:
        upsert_documents(client, df, collection_name)

        assert mock_upsert_document.call_count == len(df)
        for i, row in df.iterrows():
            mock_upsert_document.assert_any_call(
                name=str(row["id"]),
                document_base64=row["image_base64"],
                metadata={
                    "doc_id": str(row["id"]),
                    "image_file_name": row["image_filename"],
                },
                collection_name=collection_name,
                wait=False,
            )


def test_upsert_documents_returns_list_of_documents(client, df, collection_name):
    mock_collection = MagicMock()
    mock_collection.name = collection_name
    client.list_collections.return_value = [mock_collection]
    client.list_documents.return_value = [{"id": 1}, {"id": 2}]

    result = upsert_documents(client, df, collection_name)
    assert result == [{"id": 1}, {"id": 2}]
    client.list_documents.assert_called_once_with(collection_name)


def test_upsert_documents_progress_bar(client, df, collection_name, mocker):
    tqdm_mock = mocker.patch("src.document_manager.tqdm", wraps=tqdm)
    mock_collection = MagicMock()
    mock_collection.name = collection_name
    client.list_collections.return_value = [mock_collection]

    with patch.object(client, "upsert_document"):
        upsert_documents(client, df, collection_name)

    tqdm_mock.assert_called_once_with(range(len(df)), desc="Upserting documents")
