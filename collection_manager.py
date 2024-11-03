from src.client import get_colivara_client


def list_collections(client) -> list:
    """
    Lists all collections available in the Colivara client.

    Args:
        client: The Colivara client instance.

    Returns:
        list: List of collection names.
    """
    return [col.name for col in client.list_collections()]


def delete_collection(client, collection_name: str) -> None:
    """
    Deletes a specified collection from the Colivara client.

    Args:
        client: The Colivara client instance.
        collection_name (str): The name of the collection to delete.

    Raises:
        ValueError: If the collection does not exist.
    """
    if collection_name not in list_collections(client):
        raise ValueError(f"Collection '{collection_name}' does not exist.")

    client.delete_collection(collection_name)
    print(f"Collection '{collection_name}' successfully deleted.")


if __name__ == "__main__":
    import argparse

    client = get_colivara_client()

    parser = argparse.ArgumentParser(description="Manage collections in Colivara.")
    parser.add_argument("--delete", type=str, help="Name of the collection to delete.")
    parser.add_argument("--list", action="store_true", help="List all collections.")

    args = parser.parse_args()

    if args.list:
        collections = list_collections(client)
        print("Available collections:", collections)

    if args.delete:
        try:
            delete_collection(client, args.delete)
        except ValueError as e:
            print(e)
