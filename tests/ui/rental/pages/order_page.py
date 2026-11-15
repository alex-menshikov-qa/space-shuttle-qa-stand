import allure

from data import Links
from pages.base_page import BasePage
from locators.order_page_locators import OrderPageLocators, MetroLocators, FieldsLocators, ButtonsLocators


class OrderPage(BasePage):

    def open_order_page(self, locator):
        with allure.step(f"Opening the order page"):
            self.scroll_to_the_area(locator)
            self.click_element(locator)

    def load_for_whom_page(self):
        with allure.step(f"Loading the first order page"):
            self.wait_for_element_visible(OrderPageLocators.FOR_WHOM_WINDOW)

    def enter_first_name(self, name_data):
        with allure.step(f"Entering the first name {name_data}"):
            self.enter_text(FieldsLocators.FIRST_NAME_FIELD, name_data)

    def enter_last_name(self, last_name_data):
        with allure.step(f"Entering the last name {last_name_data}"):
            self.enter_text(FieldsLocators.LAST_NAME_FIELD, last_name_data)

    def enter_address(self, address_data):
        with allure.step(f"Entering the address {address_data}"):
            self.enter_text(FieldsLocators.ADDRESS_FIELD, address_data)

    def enter_station(self, metro_name):
        with allure.step(f"Choosing the metro station {metro_name}"):
            self.enter_text(MetroLocators.METRO_STATION_FIELD, metro_name)
            self.click_element(MetroLocators.get_metro_station_locator(metro_name))

    def enter_phone(self, phone_data):
        with allure.step(f"Entering the phone {phone_data}"):
            self.enter_text(FieldsLocators.PHONE_FIELD, phone_data)

    def proceed_order(self):
        with allure.step(f"Proceeding to the next page"):
            self.click_element(ButtonsLocators.DALEE_BUTTON)

    def load_about_rent_page(self):
        with allure.step(f"Loading the second order page"):
            self.wait_for_element_visible(OrderPageLocators.ABOUT_RENT_WINDOW)

    def enter_date(self, date_data):
        with allure.step(f"Choosing the date {date_data}"):
            self.enter_text(FieldsLocators.DATE_FIELD, date_data)
            self.click_element(OrderPageLocators.ABOUT_RENT_WINDOW)

    def choose_period(self, num):
        with allure.step(f"Choosing the rental period"):
            self.click_element(FieldsLocators.RENTAL_PERIOD_FIELD)
            rental_choice_formatted = self.locator_formatting(FieldsLocators.RENTAL_PERIOD_CHOICE, num)
            self.click_element(rental_choice_formatted)

    def complete_order(self):
        with allure.step(f"Completing the order"):
            self.click_element(ButtonsLocators.INSIDE_ORDER_BUTTON)

    def load_checking_window(self):
        with allure.step(f"Loading the checking modal window"):
            self.wait_for_element_visible(OrderPageLocators.CHECKING_WINDOW_TEXT)

    def submit_order(self):
        with allure.step(f"Submitting the order"):
            self.click_element(ButtonsLocators.INSIDE_YES_BUTTON)

    def get_confirmation_window(self):
        with allure.step(f"Getting the confirmation modal window"):
            element = self.find_element(OrderPageLocators.CONFIRMATION_WINDOW, 10)
            return element
