from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from add.config import Config
from add.locators import ButtonsLocators, ShipyardPageLocators, HomePageLocators


class TestAccountToShipyardSwitching:
    def test_account_shipyard_button_click(self, driver):
        driver.get(Config.SHIPYARD_URL)
        driver.find_element(*ButtonsLocators.ENTER_ACCOUNT_BUTTON).click()
        WebDriverWait(driver, 3).until(
            expected_conditions.visibility_of_element_located(ButtonsLocators.ENTER_BUTTON))

        driver.find_element(*ButtonsLocators.SHIPYARD_BUTTON).click()

        shipyard_title = WebDriverWait(driver, 3).until(
            expected_conditions.visibility_of_element_located(ShipyardPageLocators.SHIPYARD_PAGE))

        assert shipyard_title.is_displayed()

    def test_account_logo_click(self, driver):
        driver.get(Config.SHIPYARD_URL)
        driver.find_element(*ButtonsLocators.ENTER_ACCOUNT_BUTTON).click()
        WebDriverWait(driver, 3).until(
            expected_conditions.visibility_of_element_located(ButtonsLocators.ENTER_BUTTON))

        driver.find_element(*ButtonsLocators.LOGO_BUTTON).click()

        home_title = WebDriverWait(driver, 3).until(
            expected_conditions.visibility_of_element_located(HomePageLocators.HOME_PAGE))

        assert home_title.is_displayed()
