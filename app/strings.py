"""Every user-visible string of the stand lives here (plus the templates).

The story PR re-skins the stand by editing this module and the templates only.
"""

# --- OpenAPI / Swagger ---
APP_TITLE = "QA Test Stand"
APP_DESCRIPTION = "Portfolio test stand for API and UI test automation. Not production."

# --- Field validation (shared by API and web forms) ---
NAME_REQUIRED = "Name is required"
EMAIL_REQUIRED = "Email is required"
EMAIL_INVALID = "Invalid email"
PASSWORD_REQUIRED = "Password is required"
PASSWORD_INVALID = "Invalid password"

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
