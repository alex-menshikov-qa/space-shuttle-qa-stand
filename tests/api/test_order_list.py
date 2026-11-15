import allure
import requests


@allure.suite("Order Management")
@allure.title("Test retrieval of order list")
class TestGetOrderList:

    @allure.title("Get list of orders successfully")
    @allure.step("Send GET request to retrieve the list of orders")
    def test_get_orders_response_list(self, config):
        url = f"{config}/api/v1/orders"
        response = requests.get(url)
        response_json = response.json()

        with allure.step("Check that 'orders' key is present in the response"):
            assert 'orders' in response_json, "'orders' key should be present in the response"

        with allure.step("Validate that 'orders' contains a list"):
            assert isinstance(response_json['orders'], list), "Response should contain a list of orders"
