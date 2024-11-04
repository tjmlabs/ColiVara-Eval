import pandas as pd
import base64


def read_pickle_file(file_path: str) -> pd.DataFrame:
    """
    Read a pickle file and return a dataframe.

    Args:
        file_path (str): The path to the pickle file.

    Returns:
        pd.DataFrame: A dataframe loaded from the pickle file.

    Raises:
        FileNotFoundError: If the file at the specified path is not found.
        RuntimeError: If there is an error loading the data.
    """
    try:
        return pd.read_pickle(file_path).reset_index().rename(columns={"index": "id"})
    except FileNotFoundError:
        raise FileNotFoundError(f"The file at {file_path} was not found.")
    except Exception as e:
        raise RuntimeError(f"Failed to load data: {e}")


def process_data(df: pd.DataFrame, nrows: int = None) -> pd.DataFrame:
    """
    Process the dataframe by selecting rows and encoding images to base64.

    Args:
        df (pd.DataFrame): The dataframe to process.
        nrows (int, optional): Number of rows to process from the data. If None, all rows are processed.

    Returns:
        pd.DataFrame: A dataframe with an additional 'image_base64' column.
    """
    if nrows is not None:
        df = df.head(nrows).copy()  # Create a copy to avoid warnings

    df.loc[:, "image_base64"] = df["image"].apply(
        lambda x: base64.b64encode(x["bytes"]).decode("utf-8")
    )

    return df


def load_data(file_path: str, nrows: int = None) -> pd.DataFrame:
    df = read_pickle_file(file_path)
    return process_data(df, nrows)
