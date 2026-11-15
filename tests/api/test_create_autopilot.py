import pytest
import allure
import requests
from api_data import defect_enabled


pytestmark = pytest.mark.api


@allure.suite("Autopilot Creation Tests")
@allure.title("Test Create Autopilot")
class TestCreateAutopilot:

    @allure.step("Test successful autopilot registration")
    def test_create_autopilot_successfully(self, setup_and_teardown):
        payload, response = setup_and_teardown
        assert response.status_code == 201, "Expected status code 201 for successful registration"
        assert response.json() == {"ok": True}, "Response should be {'ok': True}"

    @allure.step("Test duplicate autopilot registration")
    def test_create_duplicate_autopilot(self, register_new_autopilot, setup_and_teardown):
        payload, response = setup_and_teardown
        duplicate_payload, duplicate_response = register_new_autopilot(payload)
        assert "This login is already in use" in duplicate_response.json()["message"]

    @allure.step("Test autopilot creation without some required fields")
    def test_create_autopilot_without_required_fields(self, generate_user_data, config):
        url = f"{config}/api/v1/autopilot"
        payload = {
            "password": generate_user_data['password'],
            "firstName": generate_user_data['first_name']
        }

        response = requests.post(url, json=payload)
        assert response.status_code == 400, "Expected status code 400 for missing login"
        assert response.json()['message'] == "Insufficient data to create an account"

    @allure.step("Test successful request returns 'ok:true'")
    def test_successful_request_ok_true(self, setup_and_teardown):
        payload, response = setup_and_teardown

        assert response.json() == {"ok": True}, "Response should be {'ok': True}"

    @allure.step("Test autopilot creation without login")
    def test_create_autopilot_without_login(self, generate_user_data, config):
        url = f"{config}/api/v1/autopilot"
        payload = {
            "password": generate_user_data['password'],
            "firstName": generate_user_data['first_name']
        }

        response = requests.post(url, json=payload)
        assert response.status_code == 400, "Expected status code 400 for missing login"

    @allure.step("Test autopilot creation without password")
    def test_create_autopilot_without_password(self, generate_user_data, config):
        url = f"{config}/api/v1/autopilot"
        payload = {
            "login": generate_user_data['login'],
            "firstName": generate_user_data['first_name']
        }

        response = requests.post(url, json=payload)
        assert response.status_code == 400, "Expected status code 400 for missing password"

    @pytest.mark.xfail(
        defect_enabled("MISSING_NAME_409"),
        reason="Seeded defect BUG_MISSING_NAME_409: registration without firstName returns 409 instead of 400",
        raises=AssertionError,
        strict=True,
    )
    @allure.step("Test autopilot creation without first name")
    def test_create_autopilot_without_first_name(self, generate_user_data, config):
        url = f"{config}/api/v1/autopilot"
        payload = {
            "login": generate_user_data['login'],
            "password": generate_user_data['password'],
        }

        response = requests.post(url, json=payload)
        assert response.status_code == 400, "Expected status code 400 for missing first name"

    @allure.step("Test autopilot with existent login")
    def test_create_autopilot_existent_login(self, register_new_autopilot, setup_and_teardown):
        payload, response = setup_and_teardown
        duplicate_payload, duplicate_response = register_new_autopilot(payload)
        assert duplicate_response.status_code == 409, "Expected status code 409 for existent login name"
