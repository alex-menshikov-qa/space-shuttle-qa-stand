from selenium.webdriver.common.by import By


class OrderPageLocators:
    FOR_WHOM_WINDOW = By.XPATH, "//h1[@data-testid='order-title' and normalize-space()='For Whom is the Shuttle']"
    ABOUT_RENT_WINDOW = By.XPATH, "//h1[@data-testid='order-title' and normalize-space()='About Rent']"
    CHECKING_WINDOW_TEXT = By.XPATH, "//p[@data-testid='order-confirm-text']"
    CONFIRMATION_WINDOW = By.XPATH, "//p[@data-testid='order-success-text']"


class ButtonsLocators:
    UPPER_ORDER_BUTTON = By.XPATH, "//a[@data-testid='header-order-button']"
    LOWER_ORDER_BUTTON = By.XPATH, "//a[@data-testid='home-order-button']"
    NEXT_BUTTON = By.XPATH, "//button[@data-testid='order-next-button']"
    INSIDE_ORDER_BUTTON = By.XPATH, "//button[@data-testid='order-submit-button']"
    INSIDE_YES_BUTTON = By.XPATH, "//button[@data-testid='order-confirm-yes-button']"


class FieldsLocators:
    FIRST_NAME_FIELD = By.XPATH, "//input[@data-testid='order-name-input']"
    LAST_NAME_FIELD = By.XPATH, "//input[@data-testid='order-last-name-input']"
    ADDRESS_FIELD = By.XPATH, "//input[@data-testid='order-address-input']"
    PHONE_FIELD = By.XPATH, "//input[@data-testid='order-phone-input']"
    DATE_FIELD = By.XPATH, "//input[@data-testid='order-date-input']"
    RENTAL_PERIOD_FIELD = By.XPATH, "//button[@data-testid='order-period-dropdown']"
    RENTAL_PERIOD_CHOICE = By.XPATH, "//ul[@data-testid='order-period-list']/li[normalize-space()='{}']"


class StationLocators:
    STATION_FIELD = By.XPATH, "//input[@data-testid='order-station-input']"

    @staticmethod
    def get_station_locator(station_name):
        return By.XPATH, f"//ul[@data-testid='order-station-list']/li[normalize-space()='{station_name}']"
