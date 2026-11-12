from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from add.config import Config
from add.locators import SigningLocators, ButtonsLocators


class TestEnteringAccountPage:
    def test_enter_account_button(self, driver, credentials):
        email, password = credentials
        driver.get(Config.URL)
        driver.find_element(*ButtonsLocators.PERSONAL_ACCOUNT_BUTTON).click()
        WebDriverWait(driver, 3).until(
            expected_conditions.visibility_of_element_located(ButtonsLocators.ENTER_BUTTON))

        driver.find_element(*SigningLocators.EMAIL_FIELD).send_keys(email)

        driver.find_element(*SigningLocators.PASSWORD_FIELD).send_keys(password)

        driver.find_element(*ButtonsLocators.ENTER_BUTTON).click()

        WebDriverWait(driver, 3).until(
            expected_conditions.visibility_of_element_located(ButtonsLocators.ORDER_SHUTTLE_BUTTON))

        driver.find_element(*ButtonsLocators.PERSONAL_ACCOUNT_BUTTON).click()

        logout_button = WebDriverWait(driver, 3).until(
                    expected_conditions.visibility_of_element_located(ButtonsLocators.LOGOUT_BUTTON))

        assert logout_button.is_displayed()