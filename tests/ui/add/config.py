import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    URL = os.getenv("BASE_URL", "http://localhost:8000")
    SHIPYARD_URL = f"{URL}/shipyard"
    # Test account for login / logout flows — set via environment, never hard-coded
    TEST_EMAIL = os.getenv("TEST_EMAIL")
    TEST_PASSWORD = os.getenv("TEST_PASSWORD")