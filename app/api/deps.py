"""FastAPI dependencies for authentication and authorisation."""

import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import AuthenticationError, AuthorizationError
from app.models.user import User, UserRole
from app.repositories.user import user_repo
from app.services.auth import decode_token

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode the Bearer token and return the authenticated user.

    Raises
    ------
    AuthenticationError
        If the token is missing, expired, or invalid.
    """
    if credentials is None:
        raise AuthenticationError("Not authenticated")

    user_id = decode_token(credentials.credentials, expected_type="access")

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError as exc:
        raise AuthenticationError("Invalid token subject format") from exc

    user = await user_repo.get_by_id(db, user_uuid)
    if not user:
        raise AuthenticationError("User not found")
    if not user.is_active:
        raise AuthenticationError("Account is disabled")

    return user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Guard that allows only users with the ``admin`` role.

    Raises
    ------
    AuthorizationError
        If the authenticated user is not an admin.
    """
    if current_user.role != UserRole.admin:
        raise AuthorizationError("Admin access required")
    return current_user
