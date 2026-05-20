"""User SQLAlchemy model."""

import enum

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UserRole(str, enum.Enum):
    """Role assigned to a user account."""

    admin = "admin"
    user = "user"


class User(Base):
    """Registered user account.

    Columns
    -------
    email           Unique login identifier.
    hashed_password bcrypt hash of the raw password.
    full_name       Display name (optional).
    role            RBAC role — ``admin`` or ``user`` (default).
    is_active       Soft-disable flag; inactive users cannot log in.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        default=UserRole.user,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
