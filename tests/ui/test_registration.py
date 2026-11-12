from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from add.locators import SigningLocators, ButtonsLocators
from add.helpers import get_sign_up_data
from add.config import Config

class TestRegistration:
    def test_sign_up_page(self, driver, register_page):
        assert driver.current_url == f"{Config.URL}/register", 'Url is wrong'

    def test_sign_up(self, driver, register_page):
        name_data, email_data, password_data = get_sign_up_data()

        driver.find_element(*SigningLocators.NAME_FIELD).send_keys(name_data)

        driver.find_element(*SigningLocators.EMAIL_FIELD).send_keys(email_data)

        driver.find_element(*SigningLocators.PASSWORD_FIELD).send_keys(password_data)

        driver.find_element(*ButtonsLocators.REGISTER_BUTTON).click()

        enter_button = WebDriverWait(driver, 3).until(
            expected_conditions.visibility_of_element_located(ButtonsLocators.ENTER_BUTTON))

        assert enter_button.is_displayed()

    def test_name_field_empty(self, driver, register_page):

        current_url = driver.current_url

        name_data, email_data, password_data = get_sign_up_data()

        driver.find_element(*SigningLocators.NAME_FIELD).send_keys('')

        driver.find_element(*SigningLocators.EMAIL_FIELD).send_keys(email_data)

        driver.find_element(*SigningLocators.PASSWORD_FIELD).send_keys(password_data)

        driver.find_element(*ButtonsLocators.REGISTER_BUTTON).click()

        WebDriverWait(driver, 3).until(
            expected_conditions.visibility_of_element_located(SigningLocators.NAME_ERROR))

        assert driver.current_url == current_url

    def test_email_field_wrong_format(self, driver, register_page):

        current_url = driver.current_url

        name_data, email_data, password_data = get_sign_up_data()

        driver.find_element(*SigningLocators.NAME_FIELD).send_keys(name_data)

        driver.find_element(*SigningLocators.EMAIL_FIELD).send_keys('pochtagmailcom')

        driver.find_element(*SigningLocators.PASSWORD_FIELD).send_keys(password_data)

        driver.find_element(*ButtonsLocators.REGISTER_BUTTON).click()

        WebDriverWait(driver, 3).until(
            expected_conditions.visibility_of_element_located(SigningLocators.EMAIL_ERROR))

        assert driver.current_url == current_url

    def test_password_field_3_letters(self, driver, register_page):
        current_url = driver.current_url

        name_data, email_data, password_data = get_sign_up_data()

        driver.find_element(*SigningLocators.NAME_FIELD).send_keys(name_data)

        driver.find_element(*SigningLocators.EMAIL_FIELD).send_keys(email_data)

        driver.find_element(*SigningLocators.PASSWORD_FIELD).send_keys('123')

        driver.find_element(*ButtonsLocators.REGISTER_BUTTON).click()

        WebDriverWait(driver, 3).until(
            expected_conditions.visibility_of_element_located(SigningLocators.WRONG_PASSWORD))

        assert driver.current_url == current_url

    def test_password_field_error_text(self, driver, register_page):

        name_data, email_data, password_data = get_sign_up_data()

        driver.find_element(*SigningLocators.NAME_FIELD).send_keys(name_data)

        driver.find_element(*SigningLocators.EMAIL_FIELD).send_keys(email_data)

        driver.find_element(*SigningLocators.PASSWORD_FIELD).send_keys('123')

        driver.find_element(*ButtonsLocators.REGISTER_BUTTON).click()

        error_text = WebDriverWait(driver, 3).until(
            expected_conditions.visibility_of_element_located(SigningLocators.WRONG_PASSWORD))

        assert error_text.text == "Invalid password"


