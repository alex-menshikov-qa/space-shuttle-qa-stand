import allure
import pytest
from data import LoginData


pytestmark = pytest.mark.ui

class TestOrderPage:

    @allure.title('Verify Successful Order Creation')
    @allure.description('Verifying successful order creation with two different data sets and two entry points')
    @pytest.mark.parametrize(
        'entrance,name,surname,address,station,phone,date,period',
        (
                [
                    LoginData.LOGIN_PAGE_ENTRANCE[0], LoginData.FIRST_NAME[0],
                    LoginData.LAST_NAME[0], LoginData.ADDRESS[0], LoginData.STATION[0], LoginData.PHONE[0],
                    LoginData.RENTAL_DATE[0], LoginData.RENTAL_PERIOD[0]
                ],
                [
                    LoginData.LOGIN_PAGE_ENTRANCE[1], LoginData.FIRST_NAME[1],
                    LoginData.LAST_NAME[1], LoginData.ADDRESS[1], LoginData.STATION[1], LoginData.PHONE[1],
                    LoginData.RENTAL_DATE[1], LoginData.RENTAL_PERIOD[1]
                ]
        )
    )
    def test_order(self, driver, order_page, entrance, name, surname, address, station, phone, date, period):
        order_page.open_order_page(entrance)
        order_page.load_for_whom_page()
        order_page.enter_first_name(name)
        order_page.enter_last_name(surname)
        order_page.enter_address(address)
        order_page.enter_station(station)
        order_page.enter_phone(phone)
        order_page.proceed_order()
        order_page.load_about_rent_page()
        order_page.enter_date(date)
        order_page.choose_period(period)
        order_page.complete_order()
        order_page.load_checking_window()
        order_page.submit_order()

        confirmation_window = order_page.get_confirmation_window()
        assert confirmation_window.is_displayed(), "Confirmation window didn't appear!"

