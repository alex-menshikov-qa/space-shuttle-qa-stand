import os

from dotenv import load_dotenv

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
            "metroStation": "Metro Station",
            "phone": "+7234567890",
            "rentTime": 5,
            "deliveryDate": "2024-09-30",
            "comment": "Please leave at the front door",
        }
