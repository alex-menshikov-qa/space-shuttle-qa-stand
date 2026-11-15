import os

from locators.order_page_locators import ButtonsLocators
from datetime import date, timedelta


def future_date(days):
    return (date.today() + timedelta(days=days)).strftime("%d.%m.%Y")


class Links:
    URL = os.getenv("BASE_URL", "http://localhost:8000")
    HOLONET_URL = f"{URL}/holonet"


class Answers:
    ANSWER_1 = 'One day costs 400 credits. You pay the autopilot on arrival, in credits or by card.'
    ANSWER_2 = 'One order, one shuttle. Want a fleet? Place several orders in a row; the autopilots enjoy the company.'
    ANSWER_3 = 'From the moment the autopilot hands you the shuttle. Rent for one day at 16:30 on the 8th, and the rental ends at 16:30 on the 9th.'
    ANSWER_4 = 'Only from tomorrow. Our autopilots like to plan their evenings.'
    ANSWER_5 = 'Not yet. If you need more time, call support at 0101.'
    ANSWER_6 = 'Parsecs measure distance, not time. Our autopilots know that. Mostly.'
    ANSWER_7 = 'Yes, while the shuttle is still in the hangar. No fee, and no explanations required.'
    ANSWER_8 = 'Yes. Bring snacks: it is a long flight.'


class LoginData:
    LOGIN_PAGE_ENTRANCE = [ButtonsLocators.UPPER_ORDER_BUTTON, ButtonsLocators.LOWER_ORDER_BUTTON]
    FIRST_NAME = ["Meetra", "Kissa"]
    LAST_NAME = ["Skywalkers", "Terve"]
    ADDRESS = ["The Royal Promenade Theed", "Level 1313 Uscru District"]
    STATION = ["Alderaanian", "Level 1313"]
    PHONE = ["+12345678910", "1010001010"]
    RENTAL_DATE = [future_date(7), future_date(30)]
    RENTAL_PERIOD = ["two days", "one day"]
