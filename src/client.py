from colivara_py import Colivara
from src.config import API_KEY, BASE_URL


def get_colivara_client() -> Colivara:
    """
    Initializes and returns a Colivara client.

    :raises ConnectionError: If the client initialization fails.
    :return: An instance of Colivara client.
    """
    try:
        client: Colivara = Colivara(base_url=BASE_URL, api_key=API_KEY)
        return client
    except Exception as e:
        raise ConnectionError(f"Failed to initialize Colivara client: {e}")
