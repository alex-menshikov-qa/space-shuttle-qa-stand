import pytest
import requests
import random
import string
from api_data import Config


@pytest.fixture(scope="session", autouse=True)
def stand_is_up():
    try:
        requests.get(f"{Config.URL}/health", timeout=5).raise_for_status()
    except requests.RequestException:
        pytest.skip(f"Stand is not available: {Config.URL}")


@pytest.fixture
def config():
    return Config.URL


@pytest.fixture
def generate_user_data():
    def generate_random_string(length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(length))

    login = generate_random_string(10)
    password = ''.join(random.choice(string.digits) for _ in range(4))
    first_name = generate_random_string(10)

    return {
        "login": login,
        "password": password,
        "first_name": first_name
    }


@pytest.fixture
def register_new_autopilot(config, generate_user_data):
    url = f"{config}/api/v1/autopilot"

    def register(payload=None):
        if payload is None:
            payload = {
                "login": generate_user_data['login'],
                "password": generate_user_data['password'],
                "firstName": generate_user_data['first_name']
            }

        response = requests.post(url, json=payload)
        return payload, response

    return register


@pytest.fixture
def delete_autopilot(config):
    url = f"{config}/api/v1/autopilot"

    def delete(payload):
        autopilot_id = payload.get("id")
        if autopilot_id:
            response = requests.delete(f"{url}/{autopilot_id}")
            return response
        return None

    return delete


@pytest.fixture
def login_autopilot(config):
    url = f"{config}/api/v1/autopilot/login"

    def login(payload):
        response = requests.post(url, json=payload)
        return response

    return login


@pytest.fixture
def setup_and_teardown(register_new_autopilot, login_autopilot, delete_autopilot):
    payload, response = register_new_autopilot()

    yield payload, response

    login_response = login_autopilot({"login": payload["login"], "password": payload["password"]})
    if login_response.status_code == 200:
        delete_autopilot({"id": login_response.json()["id"]})
