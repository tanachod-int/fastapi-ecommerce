"""User service — business logic for user management."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.user import User
from app.repositories.user import user_repo
from app.schemas.user import UserUpdate


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User:
    """Return a user by ID.

    Raises
    ------
    NotFoundError
        If no user exists with the given ID.
    """
    user = await user_repo.get_by_id(db, user_id)
    if not user:
        raise NotFoundError("User", str(user_id))
    return user


async def list_users(
    db: AsyncSession, *, limit: int = 20, offset: int = 0
) -> list[User]:
    """Return a paginated list of all users (admin only)."""
    return await user_repo.get_all(db, limit=limit, offset=offset)


async def update_me(db: AsyncSession, user: User, payload: UserUpdate) -> User:
    """Apply allowed profile updates to *user* and return the updated instance."""
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        return user
    return await user_repo.update(db, user, **changes)
