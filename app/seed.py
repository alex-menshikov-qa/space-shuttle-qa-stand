"""Idempotent seed, run on every container start (see entrypoint.sh).

- the test user from TEST_NAME / TEST_EMAIL / TEST_PASSWORD: created if
  missing, otherwise its password is re-synced with the environment;
- stations from app/data/stations.json: the table mirrors the file;
- fleet autopilots from app/data/fleet.json with the password FLEET_PASSWORD:
  created if missing, otherwise first name and password are re-synced.
"""

import sys

from sqlalchemy import select

from app import security, story_data, validation
from app.config import get_settings
from app.db import SessionLocal
from app.models import Autopilot, Station
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


def seed_stations() -> str:
    wanted = {item["number"]: item for item in story_data.load("stations")}
    with SessionLocal() as session:
        existing = {station.number: station for station in session.scalars(select(Station))}
        for number, item in wanted.items():
            station = existing.get(number)
            if station is None:
                session.add(Station(number=number, name=item["name"], color=item["color"]))
            else:
                station.name, station.color = item["name"], item["color"]
        for number, station in existing.items():
            if number not in wanted:
                session.delete(station)
        session.commit()
    return f"{len(wanted)} in sync"


def seed_fleet() -> str:
    password = get_settings().fleet_password
    fleet = story_data.load("fleet")
    if not validation.autopilot_password_valid(password):
        sys.exit("Fleet seed failed: FLEET_PASSWORD must be exactly 4 digits")
    for item in fleet:
        if not (
            validation.autopilot_login_valid(item["login"])
            and validation.autopilot_name_valid(item["firstName"])
        ):
            sys.exit(f"Fleet seed failed: {item} breaks the autopilot rules (app/data/fleet.json)")

    created = 0
    with SessionLocal() as session:
        for item in fleet:
            autopilot = session.scalar(select(Autopilot).where(Autopilot.login == item["login"]))
            if autopilot is None:
                session.add(
                    Autopilot(
                        login=item["login"],
                        password_hash=security.hash_password(password),
                        first_name=item["firstName"],
                    )
                )
                created += 1
                continue
            autopilot.first_name = item["firstName"]
            if not security.verify_password(autopilot.password_hash, password):
                autopilot.password_hash = security.hash_password(password)
        session.commit()
    return f"{len(fleet)} autopilots, {created} created"


if __name__ == "__main__":
    print(f"Test user {validation.normalize_email(get_settings().test_email)}: {seed_test_user()}")
    print(f"Stations: {seed_stations()}")
    print(f"Fleet: {seed_fleet()}")
