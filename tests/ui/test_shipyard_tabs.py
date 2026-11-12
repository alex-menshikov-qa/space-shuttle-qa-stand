from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from add.config import Config
from add.locators import ShipyardPageLocators


class TestShipyardTabs:
    def test_hulls_tab_active_by_default(self, driver):
        driver.get(Config.SHIPYARD_URL)
        driver.find_element(*ShipyardPageLocators.HULLS_TAB)
        WebDriverWait(driver, 3).until(
            expected_conditions.visibility_of_element_located(ShipyardPageLocators.HULLS_SECTION))
        hulls_tab_selected = driver.find_element(*ShipyardPageLocators.HULLS_SELECTED)

        assert hulls_tab_selected

    def test_engines_tab_chosen(self, driver):
        driver.get(Config.SHIPYARD_URL)
        driver.find_element(*ShipyardPageLocators.ENGINES_TAB).click()
        WebDriverWait(driver, 3).until(
            expected_conditions.visibility_of_element_located(ShipyardPageLocators.ENGINES_SECTION))
        engines_tab_selected = WebDriverWait(driver, 3).until(
            expected_conditions.visibility_of_element_located(ShipyardPageLocators.ENGINES_SELECTED))

        assert engines_tab_selected.is_displayed()

    def test_modules_tab_chosen(self, driver):
        driver.get(Config.SHIPYARD_URL)
        driver.find_element(*ShipyardPageLocators.MODULES_TAB).click()
        WebDriverWait(driver, 3).until(
            expected_conditions.visibility_of_element_located(ShipyardPageLocators.MODULES_SECTION))
        modules_tab_selected = WebDriverWait(driver, 3).until(
            expected_conditions.visibility_of_element_located(ShipyardPageLocators.MODULES_SELECTED))

        assert modules_tab_selected.is_displayed()
