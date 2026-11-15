import pytest
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class BasePage:

    def __init__(self, driver):
        self.driver = driver

    def find_element(self, locator, timeout=10):
        WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
        return self.driver.find_element(*locator)

    def scroll_to_the_area(self, locator, timeout=10):
        area_to_scroll = self.find_element(locator, timeout)
        self.driver.execute_script("arguments[0].scrollIntoView();", area_to_scroll)

    def enter_text(self, locator, text):
        element = self.find_element(locator)
        element.send_keys(text)

    def click_element(self, locator, timeout=10):
        element = self.find_element(locator, timeout)
        if element:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))
            element.click()
        else:
            pytest.fail(f"Failed to click on element with locator {locator}.")

    def get_text_from_element(self, locator, timeout=10):
        element = self.find_element(locator, timeout)
        return element.text

    def wait_for_element_visible(self, locator, timeout=10):
        try:
            return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            print(f"Element with {locator} not visible after {timeout} seconds.")
            return None

    @staticmethod
    def locator_formatting(locator, num):
        method, locator = locator
        locator = locator.format(num)
        return method, locator
