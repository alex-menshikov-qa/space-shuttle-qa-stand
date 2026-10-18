"""Idempotent seed of the test user from TEST_NAME / TEST_EMAIL / TEST_PASSWORD.

Run on every container start (see entrypoint.sh): creates the user if it is
missing, otherwise re-syncs its password with the environment.
"""

import sys

from app import security, validation
from app.config import get_settings
from app.db import SessionLocal
from app.services import users


def seed_test_user() -> str:
    settings = get_settings()
    errors = validation.registration_errors(
        validation.normalize_name(settings.test_name),
        validation.normalize_email(settings.test_email),
        settings.test_password,
    )
    if errors:
        details = "; ".join(f"{field}: {message}" for field, message in errors.items())
        sys.exit(f"Test user seed failed, fix TEST_* in .env ({details})")

    with SessionLocal() as session:
        user = users.get_by_email(session, settings.test_email)
        if user is None:
            users.register(session, settings.test_name, settings.test_email, settings.test_password)
            return "created"
        if security.verify_password(user.password_hash, settings.test_password):
            return "unchanged"
        user.password_hash = security.hash_password(settings.test_password)
        session.commit()
        return "password re-synced"


if __name__ == "__main__":
    result = seed_test_user()
    print(f"Test user {validation.normalize_email(get_settings().test_email)}: {result}")
