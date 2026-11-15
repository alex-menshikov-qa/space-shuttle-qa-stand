import pytest
import allure
from api_data import defect_enabled


@allure.suite("Autopilot Login Tests")
@allure.title("Test Autopilot Login")
class TestAutopilotLogin:

    @allure.step("Test login autopilot successfully")
    def test_login_autopilot_successfully(self, setup_and_teardown, login_autopilot):
        payload, response = setup_and_teardown
        login_payload = {
            "login": payload['login'],
            "password": payload['password']
        }

        login_response = login_autopilot(login_payload)
        assert login_response.status_code == 200, "Expected status code 200 for successful login"

    @allure.step("Test login without login")
    def test_login_without_login(self, generate_user_data, login_autopilot):
        payload = {
            "password": generate_user_data['password']
        }
        response = login_autopilot(payload)
        assert response.json()['message'] == "Insufficient data to log in"

    @pytest.mark.xfail(
        defect_enabled("LOGIN_NO_PASSWORD_504"),
        reason="Seeded defect BUG_LOGIN_NO_PASSWORD_504: login without password returns 504 instead of 400",
        raises=AssertionError,
        strict=True,
    )
    @allure.step("Test login without password")
    def test_login_without_password(self, generate_user_data, login_autopilot):
        payload = {
            "login": generate_user_data['login']
        }
        response = login_autopilot(payload)
        assert response.json()['message'] == "Insufficient data to log in"

    @allure.step("Test login with invalid credentials")
    def test_login_with_invalid_credentials(self, login_autopilot):
        payload = {
            "login": "inv@/_idLogin",
            "password": "invalidPassword"
        }
        response = login_autopilot(payload)
        assert response.status_code == 404, "Expected status code 404 for incorrect login or password"

    @allure.step("Test login without one field")
    def test_login_without_one_field_error(self, generate_user_data, login_autopilot):
        payload = {
            "password": generate_user_data['password']
        }
        response = login_autopilot(payload)
        assert response.status_code == 400, "Expected status code 400 for missing field"

    @allure.step("Test login for nonexistent user")
    def test_login_for_nonexistent_user(self, login_autopilot):
        payload = {
            "login": "nonexistentUser",
            "password": "anyPassword"
        }
        response = login_autopilot(payload)
        assert response.status_code == 404, "Expected status code 404 for nonexistent user"

    @allure.step("Test successful login returns id")
    def test_successful_login_returns_id(self, setup_and_teardown, login_autopilot):
        payload, response = setup_and_teardown
        login_payload = {
            "login": payload['login'],
            "password": payload['password']
        }

        login_response = login_autopilot(login_payload)
        assert 'id' in login_response.json(), "Response should contain autopilot ID"
