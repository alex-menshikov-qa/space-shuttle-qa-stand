from selenium.webdriver.common.by import By


class OrderPageLocators:
    FOR_WHOM_WINDOW = By.XPATH, "//div[text()='Для кого самокат']" # Локатор страницы 'Для кого самокат'
    ABOUT_RENT_WINDOW = By.XPATH, "//div[text()='Про аренду']" # # Локатор страницы 'Про аренду'
    CHECKING_WINDOW_TEXT = By.XPATH, "//div[text()='Хотите оформить заказ?']" # Локатор окна 'Хотите оформить заказ?'
    CONFIRMATION_WINDOW = By.XPATH, "//div[contains(@class, 'Order_Modal')]/div[text()='Заказ оформлен']" # Локатор окна 'Заказ оформлен'


class ButtonsLocators:
    UPPER_ORDER_BUTTON = By.XPATH, "//div[contains(@class, 'Header_Nav')]/button[text()='Заказать']" # Локатор верхней кнопки 'Заказать'
    LOWER_ORDER_BUTTON = By.XPATH, "//div[contains(@class, 'Home_FinishButton__1')]/button[text()='Заказать']" # Локатор нижней кнопки 'Заказать'
    DALEE_BUTTON = By.XPATH, "//button[text()='Далее']" # Локатор кнопки создания заказа 'Далее'
    INSIDE_ORDER_BUTTON = By.XPATH, "//div[contains(@class, 'Order_Buttons')]/button[text()='Заказать']" # Локатор кнопки 'Заказать' на странице заказа
    INSIDE_YES_BUTTON = By.XPATH, "//div[contains(@class, 'Order_Buttons')]/button[text()='Да']" # Локатор кнопки 'Да' в окне подтвержения заказа


class FieldsLocators:
    FIRST_NAME_FIELD = By.XPATH, "//input[contains(@placeholder, '* Имя')]" # Локатор поля ввода имени
    LAST_NAME_FIELD = By.XPATH, "//input[contains(@placeholder, '* Фамилия')]" # Локатор поля ввода фамилии
    ADDRESS_FIELD = By.XPATH, "//input[contains(@placeholder, '* Адрес: куда привезти заказ')]" # Локатор поля ввода адреса
    PHONE_FIELD = By.XPATH, "//input[contains(@placeholder, '* Телефон: на него позвонит курьер')]" # Локатор поля ввода телефона
    DATE_FIELD = By.XPATH, "//input[contains(@placeholder, '* Когда привезти самокат')]" # Локатор поля выбора даты
    RENTAL_PERIOD_FIELD = By.XPATH, "//div[text()='* Срок аренды']" # Локатор поля выбора срока аренды
    RENTAL_PERIOD_CHOICE = By.XPATH, "//div[contains(@class, 'Dropdown-menu')]/div[text()='{}']" # Локатор с вариантами срока аренды


class MetroLocators:
    METRO_STATION_FIELD = By.XPATH, "//input[@class='select-search__input']" # Локатор поля выбора станции метро

    @staticmethod
    def get_metro_station_locator(metro_name): # Локатор c названиями станций метро
        return By.XPATH, f"//*[@class='select-search__select']//*[text()='{metro_name}']"
