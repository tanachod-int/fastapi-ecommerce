"""Authentication service — register, login, JWT management."""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import AuthenticationError, ConflictError
from app.models.user import User
from app.repositories.user import user_repo
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password helpers


def hash_password(plain: str) -> str:
    """Return the bcrypt hash of *plain*."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return ``True`` if *plain* matches the bcrypt *hashed* value."""
    return _pwd_context.verify(plain, hashed)


# ── JWT helpers


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    """Sign and return a JWT with ``sub`` and ``type`` claims."""
    expire = datetime.now(UTC) + expires_delta
    payload = {
        "sub": subject,
        "type": token_type,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: str) -> str:
    """Return a short-lived access JWT for *user_id*."""
    return _create_token(
        subject=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes),
    )


def create_refresh_token(user_id: str) -> str:
    """Return a long-lived refresh JWT for *user_id*."""
    return _create_token(
        subject=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=settings.jwt_refresh_token_expire_days),
    )


def decode_token(token: str, expected_type: str) -> str:
    """Decode *token* and return the ``sub`` claim.

    Raises
    ------
    AuthenticationError
        If the token is expired, malformed, or has the wrong ``type`` claim.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise AuthenticationError("Could not validate credentials") from exc

    token_type: str | None = payload.get("type")
    if token_type != expected_type:
        raise AuthenticationError("Invalid token type")

    sub: str | None = payload.get("sub")
    if sub is None:
        raise AuthenticationError("Token missing subject claim")

    return sub


def _make_token_pair(user_id: str) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


# ── Service functions


async def register(db: AsyncSession, payload: UserCreate) -> User:
    """Create a new user account.

    Raises
    ------
    ConflictError
        If a user with the same email already exists.
    """
    existing = await user_repo.get_by_email(db, payload.email)
    if existing:
        raise ConflictError("An account with this email already exists")

    return await user_repo.create(
        db,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )


async def login(db: AsyncSession, email: str, password: str) -> TokenResponse:
    """Validate credentials and return a JWT token pair.

    Raises
    ------
    AuthenticationError
        If the email is not found, the password is wrong, or the account
        is inactive.
    """
    user = await user_repo.get_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise AuthenticationError("Incorrect email or password")
    if not user.is_active:
        raise AuthenticationError("Account is disabled")

    return _make_token_pair(str(user.id))


async def refresh(db: AsyncSession, refresh_token: str) -> TokenResponse:
    """Exchange a valid refresh token for a new token pair.

    Raises
    ------
    AuthenticationError
        If the refresh token is invalid or the user no longer exists.
    """
    import uuid

    user_id = decode_token(refresh_token, expected_type="refresh")

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError as exc:
        raise AuthenticationError("Invalid token subject format") from exc

    user = await user_repo.get_by_id(db, user_uuid)
    if not user or not user.is_active:
        raise AuthenticationError("Could not validate credentials")

    return _make_token_pair(str(user.id))
