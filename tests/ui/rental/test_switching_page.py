import allure
from data import Links


class TestSwitchingPage:

    @allure.title("Verify 'Space Shuttle' Logo Redirects to Homepage")
    @allure.description("Verifying that clicking the 'Space Shuttle' logo redirects to the homepage")
    def test_click_shuttle_logo(self, driver, switching_page):
        switching_page.open_order_page()
        switching_page.load_for_whom_page()
        switching_page.click_the_shuttle_logo()
        switching_page.load_shuttle_window()
        current_url = switching_page.driver.current_url
        expected_url = f'{Links.URL}/'
        assert current_url == expected_url, "URLs are different!"

    @allure.title("Verify 'HoloNet' Logo Opens the 'HoloNet' Page in a New Tab")
    @allure.description("Verifying that clicking the 'HoloNet' logo opens the 'HoloNet' page in a new tab")
    def test_click_holonet_logo(self, driver, switching_page):
        switching_page.click_the_holonet_logo()
        switching_page.switch_to_new_window()
        switching_page.load_holonet_window()
        current_url = switching_page.driver.current_url
        expected_url = Links.HOLONET_URL
        assert current_url == expected_url, "URLs are different!"
