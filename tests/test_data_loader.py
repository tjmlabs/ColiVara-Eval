from pathlib import Path
import pytest
import pandas as pd
import base64
from src.data_loader import read_pickle_file, process_data, load_data
from typing import Any


@pytest.fixture
def sample_data():
    # Create a sample dataframe similar to the expected pickle file
    data = {"image": [{"bytes": b"sample_image_data"}], "other_column": ["sample_data"]}
    df = pd.DataFrame(data)
    return df


@pytest.fixture
def sample_pickle_file(tmp_path: Path, sample_data: pd.DataFrame):
    # Save the sample dataframe to a pickle file
    file_path = tmp_path / "sample.pkl"
    sample_data.to_pickle(file_path)
    return file_path


def test_read_pickle_file_success(sample_pickle_file: Any):
    df = read_pickle_file(sample_pickle_file)
    assert not df.empty
    assert "id" in df.columns
    assert (
        df["id"].iloc[0] == 0
    )  # Check that the index has been reset and renamed to "id"


def test_read_pickle_file_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_pickle_file("non_existent_file.pkl")


def test_read_pickle_file_runtime_error(mocker, sample_pickle_file: Any):
    mocker.patch("pandas.read_pickle", side_effect=Exception("Mocked error"))
    with pytest.raises(RuntimeError, match="Failed to load data: Mocked error"):
        read_pickle_file(sample_pickle_file)


def test_process_data_all_rows(sample_data: pd.DataFrame):
    df = process_data(sample_data)
    assert "image_base64" in df.columns
    assert df["image_base64"].iloc[0] == base64.b64encode(b"sample_image_data").decode(
        "utf-8"
    )


def test_process_data_nrows(sample_data: pd.DataFrame):
    df = process_data(sample_data, nrows=1)
    assert len(df) == 1
    assert "image_base64" in df.columns
    assert df["image_base64"].iloc[0] == base64.b64encode(b"sample_image_data").decode(
        "utf-8"
    )


def test_process_data_no_image_column():
    df = pd.DataFrame({"other_column": ["sample_data"]})
    with pytest.raises(KeyError):
        process_data(df)


def test_load_data_all_rows(sample_pickle_file: Any):
    df = load_data(sample_pickle_file)
    assert not df.empty
    assert "image_base64" in df.columns
    assert df["image_base64"].iloc[0] == base64.b64encode(b"sample_image_data").decode(
        "utf-8"
    )


def test_load_data_nrows(sample_pickle_file: Any):
    df = load_data(sample_pickle_file, nrows=1)
    assert len(df) == 1
    assert "image_base64" in df.columns


def test_load_data_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_data("non_existent_file.pkl")


def test_load_data_runtime_error(mocker, sample_pickle_file: Any):
    mocker.patch("pandas.read_pickle", side_effect=Exception("Mocked error"))
    with pytest.raises(RuntimeError, match="Failed to load data: Mocked error"):
        load_data(sample_pickle_file)
