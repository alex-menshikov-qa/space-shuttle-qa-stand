from selenium.webdriver.common.by import By


class MainPageLocators:
    QUESTIONS_AREA = By.XPATH, "//*[@id='accordion__heading-7']"
    QUESTION_LOCATOR = By.XPATH, "//*[@id='accordion__heading-{}']/parent::div"
    ANSWER_LOCATOR = By.XPATH, "//div[@id='accordion__panel-{}']"
    COOKIE_BUTTON = By.XPATH, "//button[@id='home-cookie-accept-button']"
    SAMOKAT_LOGO = By.XPATH, "//a[@data-testid='header-logo-link']"
    YANDEX_LOGO = By.XPATH, "//a[@data-testid='header-holonet-link']"

