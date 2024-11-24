from tqdm import tqdm
import pandas as pd
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_fixed
import base64
from io import BytesIO

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



# if a job failed midway - you can manually adjust start_idx
def upsert_documents(
    client: Any, df: pd.DataFrame, collection_name: str, start_idx: int = 0
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
    for i in tqdm(range(start_idx, len(df)), desc="Upserting documents"):
        # convert image to base64. image looks like this: <PIL.PngImagePlugin.PngImageFile image mode=RG...
        pil_image = df.iloc[i]["image"]
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        # the reason why do this here, instead of in the data_loader.py, 
        # is because we want to avoid manipulating the dataset coming from huggingface datasets
        base64_image = base64.b64encode(buffered.getvalue()).decode()
        upsert_document(
            name=str(df.iloc[i]["id"]),
            base64_image=base64_image,
            metadata={
                "doc_id": str(df.iloc[i]["id"]),
                "image_file_name": df["image_filename"][i],
            },
            collection_name=collection_name,
            client=client,
        )
    return client.list_documents(collection_name)


@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
def upsert_document(name, base64_image, metadata, collection_name, client):
    """
    Upsert a single document into the specified collection in the client's database.

    Args:
        name (str): The name of the document.
        base64_image (str): The base64-encoded image.
        metadata (Dict[str, Any]): Metadata for the document.
        collection_name (str): The name of the collection to upsert the document into.
        client (Any): The database client.
    """
    
    success = client.upsert_document(
        name=name,
        document_base64=base64_image,
        metadata=metadata,
        collection_name=collection_name,
        wait=True,
    )

    if not success:
        raise RuntimeError(f"Failed to upsert document {name} into {collection_name} - retrying...")
