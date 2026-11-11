"""Every user-visible string of the stand lives here (plus the templates).

The story PR re-skins the stand by editing this module and the templates only.
"""

# --- OpenAPI / Swagger, page titles ---
APP_TITLE = "Space Shuttle Inc"
APP_DESCRIPTION = (
    "Space Shuttle Inc: a portfolio test stand for API and UI test automation. Not production."
)

# --- Field validation (shared by API and web forms) ---
NAME_REQUIRED = "Name is required"
NAME_TOO_LONG = "Name is too long"
EMAIL_REQUIRED = "Email is required"
EMAIL_INVALID = "Invalid email"
EMAIL_TOO_LONG = "Email is too long"
PASSWORD_REQUIRED = "Password is required"
PASSWORD_INVALID = "Invalid password"
PASSWORD_TOO_LONG = "Password is too long"

# Body-level problems that only the JSON API can have.
FIELD_REQUIRED = "Field '{field}' is required"
FIELD_INVALID = "Field '{field}' must be a string"
BODY_INVALID = "Request body must be a JSON object"

# --- Accounts ---
EMAIL_TAKEN = "User with this email already exists"
LOGIN_FAILED = "Invalid email or password"
NOT_AUTHENTICATED = "Not authenticated"
TOKEN_INVALID = "Invalid or expired token"

# --- Autopilots API (texts are verbatim from the 2023 checklists) ---
AUTOPILOT_CREATE_INSUFFICIENT = "Insufficient data to create an account"
AUTOPILOT_LOGIN_TAKEN = "This login is already in use. Please try another one"
AUTOPILOT_LOGIN_INSUFFICIENT = "Insufficient data to log in"
AUTOPILOT_ACCOUNT_NOT_FOUND = "Account not found"
AUTOPILOT_DELETE_INSUFFICIENT = "Insufficient data to delete the autopilot"
AUTOPILOT_NO_SUCH_ID = "There is no autopilot with such id"
AUTOPILOT_NOT_FOUND = "Autopilot with identifier {autopilot_id} not found"

# --- Orders API ---
ORDER_SEARCH_INSUFFICIENT = "Insufficient data to perform the search"
ORDER_NOT_FOUND = "Order not found"
ORDER_NO_SUCH_ID = "There is no order with such id"
ORDER_IN_PROGRESS = "This order is already in progress"
ORDER_CANNOT_FINISH = "This order cannot be finished"

# --- Order fields (shared by the API and the order form) ---
ORDER_NAME_INVALID = "Enter the correct name"
ORDER_LAST_NAME_INVALID = "Enter the correct last name"
ORDER_ADDRESS_INVALID = "Enter the correct address"
ORDER_STATION_INVALID = "Select a station"
ORDER_PHONE_INVALID = "Enter the correct phone number"
ORDER_DATE_INVALID = "Enter a valid date"
ORDER_PERIOD_INVALID = "Enter a valid rental period"
ORDER_COMMENT_INVALID = "Enter a valid comment"
ORDER_COLOR_INVALID = "Enter a valid color"

# --- Testing hooks (only with TEST_HOOKS=1) ---
TIME_SHIFT_INVALID = "Provide days, hours or minutes as numbers"

# --- Generic errors ---
INTERNAL_ERROR = "Internal server error"

# --- UI: header ---
# Logo "Space Shuttle Inc": only "Shuttle" is bold; "Inc" is not part of the link.
LOGO_SPACE = "Space"
LOGO_SHUTTLE = "Shuttle"
LOGO_INC = "Inc"
PARTNER_NAME = "HoloNet"
NAV_SHIPYARD = "Shipyard"
NAV_ORDER = "Order"
NAV_ORDER_STATUS = "Order Status"
NAV_ORDER_NUMBER = "Order Number"
NAV_ORDER_STATUS_GO = "Go!"
NAV_ACCOUNT = "Account"

# --- UI: form labels ---
LABEL_NAME = "Name"
LABEL_EMAIL = "Email"
LABEL_PASSWORD = "Password"

# --- UI: home (rental landing) ---
HOME_PAGE_TITLE = "Shuttle rental"
HOME_TITLE = "A shuttle that flies to you"
HOME_PITCH = (
    "Rent a shuttle on Coruscant for one to seven days. "
    "Its autopilot brings it to your door and takes it home afterwards."
)
HOME_ORDER = "Order"
HOME_FAQ_TITLE = "Questions about the important things"
COOKIE_TEXT = "We use cookies. The autopilots do not eat them, they only count them."
COOKIE_ACCEPT = "Got it"

# --- UI: HoloNet (partner stub page) ---
HOLONET_TITLE = "HoloNet News"
HOLONET_INTRO = "All of Coruscant, level by level."
HOLONET_NEWS = [
    "Traffic on level 1313 is slow again. Nobody is surprised.",
    "Space Shuttle Inc adds a ninth autopilot to its fleet.",
    "Weather control promises rain over the Senate District at noon sharp.",
]

# --- UI: shipyard (builder placeholder until the builder arrives) ---
SHIPYARD_TITLE = "Build your shuttle"
SHIPYARD_PLACEHOLDER = "The shipyard is still under construction. Hard hats on."
SHIPYARD_SIGN_IN = "Sign in"
SHIPYARD_PLACE_ORDER = "Place order"

# --- UI: order form ---
ORDER_PAGE_TITLE = "Order a shuttle"
ORDER_STEP_1_TITLE = "For Whom is the Shuttle"
ORDER_STEP_2_TITLE = "About Rent"
ORDER_FIELD_NAME = "Name"
ORDER_FIELD_LAST_NAME = "Last Name"
ORDER_FIELD_ADDRESS = "Address: where the shuttle will arrive"
ORDER_FIELD_STATION = "Shuttle Station"
ORDER_FIELD_PHONE = "Phone: the autopilot will call"
ORDER_FIELD_DATE = "When to Bring the Shuttle"
ORDER_FIELD_PERIOD = "Rental Period"
ORDER_FIELD_COLOR = "Shuttle Color"
ORDER_FIELD_COMMENT = "Comment for Autopilot"
ORDER_REQUIRED_MARK = "*"
ORDER_NEXT = "Next"
ORDER_BACK = "Back"
ORDER_SUBMIT = "Order"
ORDER_DATE_PREV_MONTH = "Previous month"
ORDER_DATE_NEXT_MONTH = "Next month"
# Index 0 is one day ... index 6 is seven days (rentTime 1-7).
RENTAL_PERIODS = [
    "one day",
    "two days",
    "three days",
    "four days",
    "five days",
    "six days",
    "seven days",
]
# API value -> label, in display order.
SHUTTLE_COLORS = {"PINKY_SWEAR": "pinky swear", "GRAY_RAINBOW": "gray rainbow"}
ORDER_CONFIRM_TEXT = "Do you want to place the order?"
ORDER_CONFIRM_YES = "Yes"
ORDER_CONFIRM_NO = "No"
ORDER_SUCCESS_TEXT = "Order number {track}. Write it down: it will come in handy to track the status"
ORDER_VIEW_STATUS = "View Status"
ORDER_SUBMIT_FAILED = "The order was not placed. Please try again."

# --- UI: order status ---
SUPPORT_PHONE = "0101"
TRACK_TITLE = "Order status"
TRACK_NUMBER = "Order Number"
TRACK_VIEW = "View"
TRACK_NOT_FOUND = "There is no such order. Are you sure you entered the correct number?"
TRACK_STATUS_HANGAR = "Shuttle in the hangar"
TRACK_STATUS_HANGAR_CAPTION = "Your autopilot is warming up for departure"
TRACK_STATUS_HEADING = "Autopilot {first_name} is heading towards you"
TRACK_STATUS_HEADING_UNASSIGNED = "Autopilot is heading towards you"
TRACK_STATUS_HEADING_CAPTION = "Contact number: {phone}"
TRACK_STATUS_ON_SITE = "Autopilot is on site"
TRACK_STATUS_ON_SITE_CAPTION = "Pick up the shuttle and pay the rental fee"
TRACK_STATUS_FLYING = "Okay, let's fly now"
TRACK_STATUS_FLYING_CAPTION = "Rental ends on {day} at {time}"  # while current
TRACK_STATUS_FLYING_CAPTION_INACTIVE = "Until the rental is over"
TRACK_STATUS_ENDED = "Rental time has ended"
# Shown only while current; the inactive status has no caption.
TRACK_STATUS_ENDED_CAPTION = (
    "{first_name} is heading home to recharge. Thanks for flying with us."
)
TRACK_STATUS_DELAYED = "Autopilot delayed"
TRACK_STATUS_DELAYED_CAPTION = (
    "We won't be able to deliver the shuttle on time. "
    "To check the status of your order, please call support at: {phone}"
)
TRACK_CANCEL = "Cancel order"
TRACK_CANCEL_CONFIRM = "Do you want to cancel the order?"
TRACK_CANCEL_BACK = "Back"
TRACK_CANCEL_CONFIRM_BUTTON = "Cancel"
TRACK_CANCELED = "Order canceled. Come back, we are always waiting for you :)"
TRACK_CANCELED_OK = "Okay"
TRACK_CANCEL_FAILED = "The order was not canceled. Please try again."

# --- UI: 404 ---
NOT_FOUND_TITLE = "Page not found"
NOT_FOUND_TEXT = "Our autopilots searched every sector. This page isn't in any of them."
NOT_FOUND_HOME_LINK = "Back to the home page"

# --- UI: register ---
REGISTER_TITLE = "Sign up"
REGISTER_SUBMIT = "Sign up"
REGISTER_LOGIN_PROMPT = "Already registered?"
REGISTER_LOGIN_LINK = "Sign in"

# --- UI: login ---
LOGIN_TITLE = "Sign in"
LOGIN_SUBMIT = "Sign in"
LOGIN_REGISTER_PROMPT = "New here?"
LOGIN_REGISTER_LINK = "Sign up"
LOGIN_FORGOT_LINK = "Forgot password?"

# --- UI: forgot password (no email is actually sent) ---
FORGOT_TITLE = "Password recovery"
FORGOT_SUBMIT = "Recover"
FORGOT_SUCCESS = "If this email is registered, recovery instructions have been sent."
FORGOT_LOGIN_PROMPT = "Remembered your password?"
FORGOT_LOGIN_LINK = "Sign in"

# --- UI: account ---
ACCOUNT_TITLE = "Account"
ACCOUNT_LOGOUT = "Log out"
