from selenium.webdriver.common.by import By


class ButtonsLocators:
    LOGOUT_BUTTON = By.CSS_SELECTOR, "[data-testid='account-logout-button']"
    REGISTER_BUTTON = By.CSS_SELECTOR, "[data-testid='register-submit-button']"
    ENTER_ACCOUNT_BUTTON = By.CSS_SELECTOR, "[data-testid='shipyard-sign-in-button']"
    PERSONAL_ACCOUNT_BUTTON = By.CSS_SELECTOR, "[data-testid='header-account-link']"
    REGISTRATION_FORM_BUTTON = By.CSS_SELECTOR, "[data-testid='register-login-link']"
    FROM_PASSWORD_RESTORE_BUTTON = By.CSS_SELECTOR, "[data-testid='forgot-password-login-link']"
    PASSWORD_RESTORE_BUTTON = By.CSS_SELECTOR, "[data-testid='login-forgot-password-link']"
    MAKE_ORDER_BUTTON = By.CSS_SELECTOR, "[data-testid='shipyard-order-button']"
    LOGO_BUTTON = By.CSS_SELECTOR, "[data-testid='header-logo-link']"
    CONSTRUCTOR_BUTTON = By.CSS_SELECTOR, "[data-testid='header-shipyard-link']"
    ENTER_BUTTON = By.CSS_SELECTOR, "[data-testid='login-submit-button']"
    REGISTER_INSTEAD_LINK = By.CSS_SELECTOR, "[data-testid='login-register-link']"


class SigningLocators:
    NAME_FIELD = By.CSS_SELECTOR, "[data-testid='register-name-input']"
    EMAIL_FIELD = By.CSS_SELECTOR, "[data-testid$='-email-input']"
    PASSWORD_FIELD = By.CSS_SELECTOR, "[data-testid$='-password-input']"
    WRONG_PASSWORD = By.CSS_SELECTOR, "[data-testid='register-password-error']"


class ConstructorPageLocators:
    BULKI_TAB = By.XPATH, "//span[text()='Булки']/parent::div" # Путь ко вкладке "Булки" на главной странице
    SOUSY_TAB = By.XPATH, "//span[text()='Соусы']/parent::div" # Путь ко вкладке "Соусы" на главной странице
    NACHINKI_TAB = By.XPATH, "//span[text()='Начинки']/parent::div" # Путь ко вкладке "Начинки" на главной странице
    SOUSY_SELECTED = By.XPATH, "//span[text()='Соусы']/parent::div[contains(@class, 'tab_tab_type_current')]" # Путь к выбранной вкладке "Булки" на главной странице
    BULKI_SELECTED = By.XPATH, "//span[text()='Булки']/parent::div[contains(@class, 'tab_tab_type_current')]" # Путь к выбранной вкладке "Соусы" на главной странице
    NACHINKI_SELECTED = By.XPATH, "//span[text()='Начинки']/parent::div[contains(@class, 'tab_tab_type_current')]" # Путь к выбранной вкладке "Начинки" на главной странице
    BULKI_SECTION = By.XPATH, "//h2[text()='Булки']" # Путь к названию секции "Булки"
    SOUSY_SECTION = By.XPATH, "//h2[text()='Соусы']" # Путь к названию секции "Соусы"
    NACHINKI_SECTION = By.XPATH, "//h2[text()='Начинки']" # Путь к названию секции "Начинки"
    CONSTRUCTOR_PAGE = By.XPATH, "//h1[text()='Соберите бургер']" # Путь к тексту "Соберите бургер" на странице конструктора



