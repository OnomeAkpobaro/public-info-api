import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Configuration class to hold environment variables
    """
    # Load environment variables from .env file
    EMAIL = os.getenv("EMAIL")

    GITHUB_URL = os.getenv("GITHUB_URL")

    API_TITLE = os.getenv("API_TITLE")
    API_DESCRIPTION = os.getenv("API_DESCRIPTION")
    API_VERSION = os.getenv("API_VERSION")

    HOST = os.getenv("HOST")
    PORT = int(os.getenv("PORT"))

    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")