"""Shipyard: the parts catalog and shuttle build orders.

A build is one hull plus any number of engines and modules. The hull is sold
in halves (top and belly plating), so it counts twice in the total. The total
is always computed here, from the catalog's own prices.
"""

import secrets
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import strings
from app.models import ShipyardOrder, ShipyardOrderItem, ShipyardPart, User

HULL = "hull"
NUMBER_MIN = 100000
NUMBER_MAX = 999999


class InvalidBuild(Exception):
    def __init__(self, message: str):
        self.message = message


def list_parts(session: Session) -> list[ShipyardPart]:
    return list(session.scalars(select(ShipyardPart).order_by(ShipyardPart.position)))


def build_total(parts: list[ShipyardPart]) -> int:
    return sum(part.price * (2 if part.category == HULL else 1) for part in parts)


def _resolve(session: Session, part_ids: Any) -> list[ShipyardPart]:
    """Ids -> catalog parts, in the given order. Raises InvalidBuild."""
    if not isinstance(part_ids, list):
        raise InvalidBuild(strings.SHIPYARD_PARTS_INVALID)
    catalog = {part.id: part for part in list_parts(session)}
    parts = []
    for part_id in part_ids:
        if isinstance(part_id, bool) or not isinstance(part_id, int) or part_id not in catalog:
            raise InvalidBuild(strings.SHIPYARD_UNKNOWN_PART.format(part_id=part_id))
        parts.append(catalog[part_id])
    hulls = sum(part.category == HULL for part in parts)
    if hulls == 0:
        raise InvalidBuild(strings.SHIPYARD_NO_HULL)
    if hulls > 1:
        raise InvalidBuild(strings.SHIPYARD_TWO_HULLS)
    return parts


def create_order(session: Session, user: User, part_ids: Any) -> ShipyardOrder:
    """Validate the build and store the order. Raises InvalidBuild."""
    parts = _resolve(session, part_ids)
    for _ in range(50):
        order = ShipyardOrder(
            number=NUMBER_MIN + secrets.randbelow(NUMBER_MAX - NUMBER_MIN + 1),
            user_id=user.id,
            total=build_total(parts),
            items=[
                ShipyardOrderItem(
                    position=position,
                    part_id=part.id,
                    category=part.category,
                    name=part.name,
                    price=part.price,
                )
                for position, part in enumerate(parts)
            ],
        )
        session.add(order)
        try:
            session.commit()
        except IntegrityError:  # the random number is taken: draw another
            session.rollback()
            continue
        return order
    raise RuntimeError("Could not allocate a free build order number")


def list_orders(session: Session, user: User) -> list[ShipyardOrder]:
    return list(
        session.scalars(
            select(ShipyardOrder).where(ShipyardOrder.user_id == user.id).order_by(ShipyardOrder.id)
        )
    )


def part_as_dict(part: ShipyardPart) -> dict:
    return {
        "id": part.id,
        "category": part.category,
        "name": part.name,
        "price": part.price,
        "description": part.description,
        "mass": part.mass,
        "power": part.power,
        "cargo": part.cargo,
        "comfort": part.comfort,
    }


def order_as_dict(order: ShipyardOrder) -> dict:
    return {
        "number": order.number,
        "total": order.total,
        "createdAt": order.created_at.isoformat(timespec="seconds"),
        "parts": [
            {"id": item.part_id, "category": item.category, "name": item.name, "price": item.price}
            for item in order.items
        ],
    }
