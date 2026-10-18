"""Every user-visible string of the stand lives here (plus the templates).

The story PR re-skins the stand by editing this module and the templates only.
"""

# --- OpenAPI / Swagger, page titles ---
APP_TITLE = "QA Test Stand"
APP_DESCRIPTION = "Portfolio test stand for API and UI test automation. Not production."

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
LOGO_TEXT = "QA Stand"
NAV_BUILDER = "Builder"
NAV_ACCOUNT = "Account"

# --- UI: form labels ---
LABEL_NAME = "Name"
LABEL_EMAIL = "Email"
LABEL_PASSWORD = "Password"

# --- UI: home ---
HOME_TITLE = "Builder"
HOME_PLACEHOLDER = "The builder will be here."
HOME_SIGN_IN = "Sign in"
HOME_PLACE_ORDER = "Place order"

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
