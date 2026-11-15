import os

from dotenv import load_dotenv
from datetime import date, timedelta

load_dotenv()


class Config:
    URL = os.getenv("BASE_URL", "http://localhost:8000")


def defect_enabled(name):
    return os.getenv(f"BUG_{name}", "").strip().lower() in ("1", "true", "yes", "on")


class OrderData:
    @staticmethod
    def get_order_data():
        return {
            "firstName": "Max",
            "lastName": "Payne",
            "address": "123 Main St",
            "station": 1,
            "phone": "+7234567890",
            "rentTime": 5,
            "deliveryDate": (date.today() + timedelta(days=7)).isoformat(),
            "comment": "Leave at the front door",
        }
