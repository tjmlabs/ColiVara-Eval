from colivara_py import Colivara
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(override=True)

def get_colivara_client() -> Colivara:
    """
    Initializes and returns a Colivara client.

    :raises ConnectionError: If the client initialization fails.
    :return: An instance of Colivara client.
    """

    API_KEY = os.getenv("COLIVARA_API_KEY")
    BASE_URL = os.getenv("COLIVARA_BASE_URL")

    if not API_KEY or not BASE_URL:
        raise EnvironmentError(
            "API_KEY or BASE_URL not found in the environment variables."
        )

    try:
        client: Colivara = Colivara(base_url=BASE_URL, api_key=API_KEY)
        print(f"Initialized Colivara client with base URL: {BASE_URL}")
        return client
    except Exception as e:
        raise ConnectionError(f"Failed to initialize Colivara client: {e}")
