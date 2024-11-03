from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("COLIVARA_API_KEY")
BASE_URL = os.getenv("COLIVARA_BASE_URL")

if not API_KEY or not BASE_URL:
    raise EnvironmentError(
        "API_KEY or BASE_URL not found in the environment variables."
    )
