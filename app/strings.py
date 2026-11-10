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

# --- UI: pages that arrive in a later stage ---
ORDER_TITLE = "Order a shuttle"
ORDER_PLACEHOLDER = "The order form is being assembled."
TRACK_TITLE = "Order status"
TRACK_PLACEHOLDER = "Order tracking is being assembled."

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
