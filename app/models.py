"""SQLAlchemy models. Alembic autogenerate reads Base.metadata."""

from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.validation import EMAIL_MAX_LENGTH, NAME_MAX_LENGTH


class Base(DeclarativeBase):
    pass


class User(Base):
    """Web account (register / login). Not related to the future pilots API."""

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
