"""Shuttle stations (seed data from app/data/stations.json)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Station


def search(session: Session, query: str | None = None) -> list[Station]:
    """Stations whose name contains `query` (case-insensitive), by number.
    No query, or an empty one, returns all of them."""
    stations = session.scalars(select(Station).order_by(Station.number)).all()
    needle = (query or "").casefold()
    return [station for station in stations if needle in station.name.casefold()]


def as_dict(station: Station) -> dict:
    return {"number": station.number, "name": station.name, "color": station.color}
