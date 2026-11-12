from selenium.webdriver.common.by import By


class ButtonsLocators:
    LOGOUT_BUTTON = By.CSS_SELECTOR, "[data-testid='account-logout-button']"
    REGISTER_BUTTON = By.CSS_SELECTOR, "[data-testid='register-submit-button']"
    ENTER_ACCOUNT_BUTTON = By.CSS_SELECTOR, "[data-testid='shipyard-sign-in-button']"
    PERSONAL_ACCOUNT_BUTTON = By.CSS_SELECTOR, "[data-testid='header-account-link']"
    REGISTRATION_FORM_BUTTON = By.CSS_SELECTOR, "[data-testid='register-login-link']"
    FROM_PASSWORD_RESTORE_BUTTON = By.CSS_SELECTOR, "[data-testid='forgot-password-login-link']"
    PASSWORD_RESTORE_BUTTON = By.CSS_SELECTOR, "[data-testid='login-forgot-password-link']"
    ORDER_SHUTTLE_BUTTON = By.CSS_SELECTOR, "[data-testid='shipyard-order-button']"
    LOGO_BUTTON = By.CSS_SELECTOR, "[data-testid='header-logo-link']"
    SHIPYARD_BUTTON = By.CSS_SELECTOR, "[data-testid='header-shipyard-link']"
    ENTER_BUTTON = By.CSS_SELECTOR, "[data-testid='login-submit-button']"
    REGISTER_INSTEAD_LINK = By.CSS_SELECTOR, "[data-testid='login-register-link']"


class SigningLocators:
    NAME_FIELD = By.CSS_SELECTOR, "[data-testid='register-name-input']"
    EMAIL_FIELD = By.CSS_SELECTOR, "[data-testid$='-email-input']"
    PASSWORD_FIELD = By.CSS_SELECTOR, "[data-testid$='-password-input']"
    WRONG_PASSWORD = By.CSS_SELECTOR, "[data-testid='register-password-error']"


class ShipyardPageLocators:
    HULLS_TAB = By.CSS_SELECTOR, "[data-testid='shipyard-tab-hulls']"  # "Hulls" tab
    ENGINES_TAB = By.CSS_SELECTOR, "[data-testid='shipyard-tab-engines']"  # "Engines" tab
    MODULES_TAB = By.CSS_SELECTOR, "[data-testid='shipyard-tab-modules']"  # "Modules" tab
    HULLS_SELECTED = By.CSS_SELECTOR, "[data-testid='shipyard-tab-hulls'][data-active='true']"  # active "Hulls" tab
    ENGINES_SELECTED = By.CSS_SELECTOR, "[data-testid='shipyard-tab-engines'][data-active='true']"  # active "Engines" tab
    MODULES_SELECTED = By.CSS_SELECTOR, "[data-testid='shipyard-tab-modules'][data-active='true']"  # active "Modules" tab
    HULLS_SECTION = By.CSS_SELECTOR, "[data-testid='shipyard-section-hulls-title']"  # "Hulls" section heading
    ENGINES_SECTION = By.CSS_SELECTOR, "[data-testid='shipyard-section-engines-title']"  # "Engines" section heading
    MODULES_SECTION = By.CSS_SELECTOR, "[data-testid='shipyard-section-modules-title']"  # "Modules" section heading
    SHIPYARD_PAGE = By.CSS_SELECTOR, "[data-testid='shipyard-title']"  # "Build your shuttle" page title


class HomePageLocators:
    HOME_PAGE = By.CSS_SELECTOR, "[data-testid='home-title']"  # "A shuttle that flies to you" landing title

