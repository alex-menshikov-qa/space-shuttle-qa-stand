import allure
from locators.main_page_locators import MainPageLocators
from pages.base_page import BasePage


class MainPage(BasePage):

    def wait_for_dropdown_load(self):
        with allure.step(f"Loading the dropdown area"):
            self.find_element(MainPageLocators.SAMOKAT_LOGO)
            self.scroll_to_the_area(MainPageLocators.QUESTIONS_AREA)

    def click_cookies(self):
        self.click_element(MainPageLocators.COOKIE_BUTTON)

    def click_question(self, num):
        with allure.step(f"Clicking the question"):
            question_locator_formatted = self.locator_formatting(MainPageLocators.QUESTION_LOCATOR, num)
            self.click_element(question_locator_formatted)

    def get_answer_text(self, num):
        with allure.step(f"Getting the answer text"):
            answer_locator_formatted = self.locator_formatting(MainPageLocators.ANSWER_LOCATOR, num)
            return self.get_text_from_element(answer_locator_formatted)

    def click_question_get_answer(self, num):
        self.click_question(num)
        return self.get_answer_text(num)

    @staticmethod
    def check_answer(result, expected):
        with allure.step(f"Verify result matches expected"):
            return result == expected

