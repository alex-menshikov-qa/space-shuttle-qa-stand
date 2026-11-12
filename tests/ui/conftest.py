from urllib.error import URLError
from urllib.request import urlopen

import os
import pytest
from selenium import webdriver
from add.config import Config
from add.locators import ButtonsLocators
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def is_base_url_available(url):
    try:
        with urlopen(url, timeout=5):
            return True
    except URLError:
        return False


@pytest.fixture
def driver():
    if not is_base_url_available(Config.URL):
        pytest.skip(f"Base URL is not available: {Config.URL}")

    options = webdriver.ChromeOptions()
    if os.getenv("CI"):
        options.add_argument("--headless=new")
    chrome = webdriver.Chrome(options=options)
    chrome.get(Config.URL)
    yield chrome
    chrome.quit()


@pytest.fixture
def register_page(driver):
    driver.get(Config.SHIPYARD_URL)
    driver.find_element(*ButtonsLocators.ENTER_ACCOUNT_BUTTON).click()
    WebDriverWait(driver, 15).until(
        expected_conditions.visibility_of_element_located(ButtonsLocators.ENTER_BUTTON))

    driver.find_element(*ButtonsLocators.REGISTER_INSTEAD_LINK).click()
    WebDriverWait(driver, 15).until(
        expected_conditions.visibility_of_element_located(ButtonsLocators.REGISTER_BUTTON))


@pytest.fixture
def credentials():
    if not (Config.TEST_EMAIL and Config.TEST_PASSWORD):
        pytest.skip("Set TEST_EMAIL and TEST_PASSWORD to run login-dependent tests")
    return Config.TEST_EMAIL, Config.TEST_PASSWORD
