"""Pytest configuration and shared fixtures."""

import os
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Force test settings before importing app modules
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/test_db"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["JWT_SECRET_KEY"] = "test-secret"

from app.config import get_settings
from app.database import get_db
from app.main import create_app
from app.models.base import Base


@pytest.fixture(scope="session")
def engine():
    """Create a test database engine."""
    # We use SQLite for quick tests, but note that some Postgres-specific
    # features (like ENUM or UUID) might need special handling if not using Postgres.
    # For a real project, consider using testcontainers with Postgres.
    # Here we mock it with an in-memory SQLite for demonstration, 
    # but since our models use postgresql.UUID, let's stick to the URL from settings 
    # and assume a local test DB or we just mock the DB entirely in tests.
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    return test_engine


@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for a single test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestingSessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession,
    )

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def app(db_session: AsyncSession):
    """Return a configured FastAPI application instance."""
    app_instance = create_app()

    # Override dependencies
    async def override_get_db():
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    app_instance.dependency_overrides[get_db] = override_get_db
    return app_instance


@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Return an async HTTP client for the FastAPI application."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
