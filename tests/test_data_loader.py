from pathlib import Path
import pytest
import pandas as pd
import base64
from src.data_loader import load_data
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


def test_load_data_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_data("non_existent_file.pkl")


def test_load_data_runtime_error(mocker, sample_pickle_file: Any):
    mocker.patch("pandas.read_pickle", side_effect=Exception("Mocked error"))
    with pytest.raises(RuntimeError, match="Failed to load data: Mocked error"):
        load_data(sample_pickle_file)
