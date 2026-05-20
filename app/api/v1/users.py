"""Users router — profile endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.repositories.user import user_repo
from app.schemas.common import DataResponse
from app.schemas.user import UserResponse, UserUpdate
from app.services import user as user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=DataResponse[UserResponse],
    summary="Get current user profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> DataResponse[UserResponse]:
    """Return the authenticated user's profile."""
    return DataResponse(data=UserResponse.model_validate(current_user))


@router.patch(
    "/me",
    response_model=DataResponse[UserResponse],
    summary="Update current user profile",
)
async def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[UserResponse]:
    """Update the authenticated user's mutable profile fields."""
    updated = await user_service.update_me(db, current_user, payload)
    return DataResponse(data=UserResponse.model_validate(updated))


@router.get(
    "",
    response_model=DataResponse[list[UserResponse]],
    summary="List all users (admin only)",
    dependencies=[Depends(require_admin)],
)
async def list_users(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> DataResponse[list[UserResponse]]:
    """Return a paginated list of all user accounts. Admin role required."""
    users = await user_service.list_users(db, limit=limit, offset=offset)
    return DataResponse(data=[UserResponse.model_validate(u) for u in users])


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user account (admin only)",
    dependencies=[Depends(require_admin)],
)
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Hard-delete a user account by ID. Admin role required."""
    user = await user_service.get_user_by_id(db, user_id)
    await user_repo.delete(db, user)
