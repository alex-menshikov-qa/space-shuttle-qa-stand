import pytest
import allure
import requests
from api_data import OrderData


@allure.suite("Order Management")
@allure.title("Test Order Creation")
class TestCreateOrder:

    @allure.title("Test creating order with different color options")
    @pytest.mark.parametrize("color, expected_status", [
        (["PINKY_SWEAR"], 201),
        (["GRAY_RAINBOW"], 201),
        (["PINKY_SWEAR", "GRAY_RAINBOW"], 201),
        ([], 201),
    ])
    @allure.step("Create order with specified color")
    def test_create_order_with_color(self, config, color, expected_status):
        url = f"{config}/api/v1/orders"
        payload = {**OrderData.get_order_data(), "color": color}

        with allure.step(f"Sending POST request with color: {color}"):
            response = requests.post(url, json=payload)

        with allure.step(f"Verifying response status code is {expected_status}"):
            assert response.status_code == expected_status, f"Expected status {expected_status}, got {response.status_code}"

    @allure.title("Test order creation and check 'track' field in response")
    @allure.step("Create order and verify 'track' field in response")
    def test_create_order_and_check_track_field(self, config):
        url = f"{config}/api/v1/orders"
        payload = {**OrderData.get_order_data(), "color": ["PINKY_SWEAR"]}

        with allure.step("Sending POST request to create order with color: PINKY_SWEAR"):
            response = requests.post(url, json=payload)

        response_json = response.json()

        with allure.step("Verifying 'track' field is present in the response"):
            assert "track" in response_json, "Response should contain 'track' field"
