"""Station search for the order form."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_session
from app.schemas import StationsResponse
from app.services import stations

router = APIRouter(prefix="/stations", tags=["stations"])


@router.get("/search")
def search(s: str | None = None, session: Session = Depends(get_session)) -> StationsResponse:
    """Stations whose name contains `s` (case-insensitive, from 1 character).
    Without `s` returns all stations."""
    found = stations.search(session, s)
    return StationsResponse(stations=[stations.as_dict(station) for station in found])
