"""Pydantic schemas for User resources."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


# ── Request Schemas


class UserCreate(BaseModel):
    """Payload to register a new user account."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(None, max_length=255)


class UserUpdate(BaseModel):
    """Payload to update the current user's profile."""

    full_name: str | None = Field(None, max_length=255)


# ── Response Schemas


class UserResponse(BaseModel):
    """Public representation of a user account."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    full_name: str | None
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
