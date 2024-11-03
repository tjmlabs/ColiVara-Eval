import pandas as pd
import base64


def load_data(file_path: str, nrows: int = None) -> pd.DataFrame:
    """
    Load data from a pickle file, process images to base64, and extract queries.

    Args:
        file_path (str): The path to the pickle file.
        nrows (int, optional): Number of rows to load from the data. If None, all rows are loaded.

    Returns:
        pd.DataFrame: A dataframe containing the original data along with an additional
        'image_base64' column containing base64 encoded images.

    Raises:
        FileNotFoundError: If the file at the specified path is not found.
        RuntimeError: If there is an error loading the data.
    """
    try:
        df = pd.read_pickle(file_path).reset_index().rename(columns={"index": "id"})

        # Select only the specified number of rows if nrows is provided
        if nrows is not None:
            df = df.head(nrows)

        # Add a new column with base64-encoded images
        df["image_base64"] = df["image"].apply(
            lambda x: base64.b64encode(x["bytes"]).decode("utf-8")
        )

        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"The file at {file_path} was not found.")
    except Exception as e:
        raise RuntimeError(f"Failed to load data: {e}")
