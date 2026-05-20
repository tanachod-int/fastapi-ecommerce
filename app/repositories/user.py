"""User repository — DB queries only, no business logic."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Async repository for the ``users`` table."""

    model = User

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Return the user with the given email address, or ``None``."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()


# Singleton — import this instance everywhere
user_repo = UserRepository()
