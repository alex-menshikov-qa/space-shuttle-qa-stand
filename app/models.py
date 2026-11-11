"""SQLAlchemy models. Alembic autogenerate reads Base.metadata."""

from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, Text, false, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.validation import EMAIL_MAX_LENGTH, NAME_MAX_LENGTH


class Base(DeclarativeBase):
    pass


class User(Base):
    """Web account (register / login). Not related to autopilots."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH))
    # Stored trimmed and lowercased, which makes uniqueness case-insensitive.
    email: Mapped[str] = mapped_column(String(EMAIL_MAX_LENGTH), unique=True)
    # argon2id hash, e.g. "$argon2id$v=19$m=65536,t=3,p=4$..."
    password_hash: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Autopilot(Base):
    """A droid employee that delivers shuttles. Managed through /api/v1/autopilot."""

    __tablename__ = "autopilots"

    id: Mapped[int] = mapped_column(primary_key=True)
    # TEXT on purpose: seeded defects may let out-of-rule values through.
    login: Mapped[str] = mapped_column(Text, unique=True)
    # argon2id hash, same as users.password_hash
    password_hash: Mapped[str] = mapped_column(Text)
    first_name: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Station(Base):
    """Shuttle station, synced from app/data/stations.json on every start."""

    __tablename__ = "stations"

    number: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(Text)
    color: Mapped[str] = mapped_column(Text)  # line color, a CSS color name


class Order(Base):
    """A rental order. Its status is not stored: it is computed from the
    timestamps below and the order's own clock (see services/orders.py)."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    track: Mapped[int] = mapped_column(Integer, unique=True)
    first_name: Mapped[str] = mapped_column(Text)
    last_name: Mapped[str] = mapped_column(Text)
    address: Mapped[str] = mapped_column(Text)
    # Station as it was when the order was placed (no foreign key: stations
    # are editable seed data).
    station_number: Mapped[int] = mapped_column(Integer)
    station_name: Mapped[str] = mapped_column(Text)
    station_color: Mapped[str] = mapped_column(Text)
    phone: Mapped[str] = mapped_column(Text)
    rent_time: Mapped[int] = mapped_column(Integer)  # days, 1-7
    delivery_date: Mapped[date] = mapped_column(Date)
    comment: Mapped[str] = mapped_column(Text, server_default="")
    color: Mapped[list[str]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # accepted_at / finished_at are taken from the order's own clock.
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # No foreign key: a deleted autopilot leaves its orders behind, flagged.
    autopilot_id: Mapped[int | None] = mapped_column(Integer, index=True)
    autopilot_first_name: Mapped[str | None] = mapped_column(Text)
    autopilot_deleted: Mapped[bool] = mapped_column(Boolean, server_default=false())
    # Seconds added to "now" for this order only (testing hook).
    clock_offset_seconds: Mapped[int] = mapped_column(Integer, server_default="0")


class ShipyardPart(Base):
    """Catalog part, synced from app/data/shipyard_parts.json on every start."""

    __tablename__ = "shipyard_parts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    position: Mapped[int] = mapped_column(Integer)  # order in the catalog file
    category: Mapped[str] = mapped_column(Text)  # hull | engine | module
    name: Mapped[str] = mapped_column(Text)
    price: Mapped[int] = mapped_column(Integer)  # credits
    description: Mapped[str] = mapped_column(Text)
    mass: Mapped[int] = mapped_column(Integer)  # t
    power: Mapped[int] = mapped_column(Integer)  # MW
    cargo: Mapped[int] = mapped_column(Integer)  # m3
    comfort: Mapped[int] = mapped_column(Integer)  # stars, 1-5
    color: Mapped[str] = mapped_column(Text)  # accent color of the picture


class ShipyardOrder(Base):
    """A shuttle build ordered by a web account. Not related to rental orders."""

    __tablename__ = "shipyard_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(Integer, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    total: Mapped[int] = mapped_column(Integer)  # computed by the server; the hull counts twice
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    items: Mapped[list["ShipyardOrderItem"]] = relationship(
        order_by="ShipyardOrderItem.position", cascade="all, delete-orphan", passive_deletes=True
    )


class ShipyardOrderItem(Base):
    """One part of a build, as it was when ordered (name and price are
    snapshots: later catalog edits never rewrite old orders)."""

    __tablename__ = "shipyard_order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("shipyard_orders.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer)
    part_id: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    price: Mapped[int] = mapped_column(Integer)
