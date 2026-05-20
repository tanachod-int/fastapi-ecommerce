"""Authentication router — register, login, token refresh."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.common import DataResponse
from app.schemas.user import UserCreate, UserResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=DataResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> DataResponse[UserResponse]:
    """Create a new user account and return the profile.

    - Email must be unique
    - Password is stored as a bcrypt hash
    """
    user = await auth_service.register(db, payload)
    return DataResponse(data=UserResponse.model_validate(user))


@router.post(
    "/login",
    response_model=DataResponse[TokenResponse],
    summary="Login and receive JWT tokens",
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> DataResponse[TokenResponse]:
    """Authenticate with email + password and receive an access/refresh token pair."""
    tokens = await auth_service.login(db, payload.email, payload.password)
    return DataResponse(data=tokens)


@router.post(
    "/refresh",
    response_model=DataResponse[TokenResponse],
    summary="Refresh access token",
)
async def refresh_token(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> DataResponse[TokenResponse]:
    """Exchange a valid refresh token for a new access/refresh token pair."""
    tokens = await auth_service.refresh(db, payload.refresh_token)
    return DataResponse(data=tokens)
