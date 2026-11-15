import allure

from data import Links
from locators.order_page_locators import OrderPageLocators, ButtonsLocators
from pages.base_page import BasePage
from locators.switching_page_locators import SwitchingPageLocators
from locators.main_page_locators import MainPageLocators


class SwitchingPage(BasePage):

    def open_order_page(self):
        with allure.step(f"Opening the side page"):
            self.driver.get(f'{Links.URL}order')

    def load_for_whom_page(self):
        with allure.step(f"Loading the side page"):
            self.wait_for_element_visible(OrderPageLocators.FOR_WHOM_WINDOW)

    def click_the_samokat_logo(self):
        with allure.step(f"Clicking the 'Самокат' logo"):
            self.click_element(MainPageLocators.SAMOKAT_LOGO)

    def load_samokat_window(self):
        with allure.step(f"Loading the 'Самокат' window"):
            self.wait_for_element_visible(MainPageLocators.SAMOKAT_LOGO)

    def click_the_yandex_logo(self):
        with allure.step(f"Clicking the 'Яндекс' logo"):
            self.click_element(MainPageLocators.YANDEX_LOGO)

    def switch_to_new_window(self):
        with allure.step(f"Switching to new window"):
            main_window = self.driver.current_window_handle
            all_windows = self.driver.window_handles

            for window in all_windows:
                if window != main_window:
                    self.driver.switch_to.window(window)
                    break

    def load_dzen_window(self):
        with allure.step(f"Loading the 'Дзен' window"):
            self.wait_for_element_visible(SwitchingPageLocators.DZEN_SEARCH_BUTTON)
