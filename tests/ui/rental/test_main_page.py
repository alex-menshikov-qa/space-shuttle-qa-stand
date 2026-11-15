import allure
import pytest
from data import Answers


class TestMainPage:

    @allure.title('Verify Answers to Questions')
    @allure.description('Verifying that clicking the question opens the corresponding answer text')
    @pytest.mark.parametrize(
        "q_num,expected_result",
        [
            (0, Answers.ANSWER_1),
            (1, Answers.ANSWER_2),
            (2, Answers.ANSWER_3),
            (3, Answers.ANSWER_4),
            (4, Answers.ANSWER_5),
            (5, Answers.ANSWER_6),
            (6, Answers.ANSWER_7),
            (7, Answers.ANSWER_8)
        ]
    )
    def test_questions(self, driver, main_page, q_num, expected_result):
        main_page.wait_for_dropdown_load()
        main_page.click_cookies()
        result = main_page.click_question_get_answer(
            q_num
        )

        assert main_page.check_answer(result, expected_result)
