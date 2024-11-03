from tqdm import tqdm
import pandas as pd
from typing import List, Dict, Any


def check_collection(client: Any, collection_name: str) -> bool:
    """
    Check if a collection exists in the client's database.

    Args:
        client (Any): The database client.
        collection_name (str): The name of the collection to check.

    Returns:
        bool: True if the collection exists, False otherwise.
    """
    collections = client.list_collections()
    return collection_name in [col.name for col in collections]


def upsert_documents(
    client: Any, df: pd.DataFrame, collection_name: str
) -> List[Dict[str, Any]]:
    """
    Upsert documents into a specified collection in the client's database.

    Args:
        client (Any): The database client.
        df (pd.DataFrame): DataFrame containing document metadata and base64 images.
        collection_name (str): The name of the collection to upsert documents into.

    Returns:
        List[Dict[str, Any]]: List of documents in the collection after upserting.
    """
    if not check_collection(client, collection_name):
        client.create_collection(collection_name)

    for i in tqdm(range(len(df)), desc="Upserting documents"):
        client.upsert_document(
            name=str(df.iloc[i]["id"]),
            document_base64=df.iloc[i]["image_base64"],
            metadata={
                "doc_id": str(df["docId"][i]),
                "image_file_name": df["image_filename"][i],
            },
            collection_name=collection_name,
            wait=False,
        )

    return client.list_documents(collection_name)
