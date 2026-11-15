import allure

from data import Links
from locators.order_page_locators import OrderPageLocators, ButtonsLocators
from pages.base_page import BasePage
from locators.switching_page_locators import SwitchingPageLocators
from locators.main_page_locators import MainPageLocators


class SwitchingPage(BasePage):

    def open_order_page(self):
        with allure.step(f"Opening the side page"):
            self.driver.get(f'{Links.URL}/order')

    def load_for_whom_page(self):
        with allure.step(f"Loading the side page"):
            self.wait_for_element_visible(OrderPageLocators.FOR_WHOM_WINDOW)

    def click_the_shuttle_logo(self):
        with allure.step(f"Clicking the 'Space Shuttle' logo"):
            self.click_element(MainPageLocators.SHUTTLE_LOGO)

    def load_shuttle_window(self):
        with allure.step(f"Loading the home page"):
            self.wait_for_element_visible(MainPageLocators.SHUTTLE_LOGO)

    def click_the_holonet_logo(self):
        with allure.step(f"Clicking the 'HoloNet' logo"):
            self.click_element(MainPageLocators.HOLONET_LOGO)

    def switch_to_new_window(self):
        with allure.step(f"Switching to new window"):
            main_window = self.driver.current_window_handle
            all_windows = self.driver.window_handles

            for window in all_windows:
                if window != main_window:
                    self.driver.switch_to.window(window)
                    break

    def load_holonet_window(self):
        with allure.step(f"Loading the 'HoloNet' page"):
            self.wait_for_element_visible(SwitchingPageLocators.HOLONET_TITLE)
