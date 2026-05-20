"""Generic async repository with common CRUD operations."""

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Async CRUD repository for a single SQLAlchemy model.

    Subclass this and pass the model class::

        class UserRepository(BaseRepository[User]):
            model = User

    All methods accept an ``AsyncSession`` as the first argument so the
    caller controls the transaction boundary.
    """

    model: type[ModelT]

    # ── Read

    async def get_by_id(
        self, db: AsyncSession, resource_id: uuid.UUID
    ) -> ModelT | None:
        """Return a single row by primary key, or ``None`` if not found."""
        result = await db.execute(select(self.model).where(self.model.id == resource_id))
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ModelT]:
        """Return a paginated list of rows (offset-based)."""
        result = await db.execute(select(self.model).limit(limit).offset(offset))
        return list(result.scalars().all())

    # ── Write

    async def create(self, db: AsyncSession, **kwargs: Any) -> ModelT:
        """Insert a new row and return the persisted instance."""
        instance = self.model(**kwargs)
        db.add(instance)
        await db.flush()   # get DB-generated values (id, timestamps)
        await db.refresh(instance)
        return instance

    async def update(
        self, db: AsyncSession, instance: ModelT, **kwargs: Any
    ) -> ModelT:
        """Patch ``instance`` with the given fields and return it."""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        db.add(instance)
        await db.flush()
        await db.refresh(instance)
        return instance

    async def delete(self, db: AsyncSession, instance: ModelT) -> None:
        """Hard-delete ``instance`` from the database."""
        await db.delete(instance)
        await db.flush()
