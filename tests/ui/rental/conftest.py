import allure
import pytest
from selenium import webdriver
from data import Links
from pages.main_page import MainPage
from pages.order_page import OrderPage
from pages.switching_page import SwitchingPage


@pytest.fixture
def driver():
    with allure.step("Create driver"):
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument('--headless')
        firefox = webdriver.Firefox(options=firefox_options)
        firefox.maximize_window()
        firefox.get(Links.URL)
    yield firefox
    with allure.step("Close driver"):
        firefox.quit()


@pytest.fixture
def main_page(driver):
    return MainPage(driver)


@pytest.fixture
def order_page(driver):
    return OrderPage(driver)


@pytest.fixture
def switching_page(driver):
    return SwitchingPage(driver)
