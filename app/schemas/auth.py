"""Pydantic schemas for authentication flows."""

from pydantic import BaseModel, EmailStr


# ── Request Schemas


class LoginRequest(BaseModel):
    """Credentials for the login endpoint."""

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Payload to exchange a refresh token for a new access token."""

    refresh_token: str


# ── Response Schemas


class TokenResponse(BaseModel):
    """JWT token pair returned after successful login or token refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
