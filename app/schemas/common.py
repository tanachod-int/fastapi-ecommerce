"""Shared schemas used across the application."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


# ── Success Response


class DataResponse(BaseModel, Generic[DataT]):
    """Standard success response wrapper.

    All successful responses are wrapped in a ``data`` key so clients
    can distinguish between a resource object and a top-level envelope.

    Example::

        {
            "data": {
                "id": "abc-123",
                "email": "alice@example.com"
            }
        }
    """

    data: DataT


# ── Error Response


class ErrorDetail(BaseModel):
    """Single field-level validation error."""

    field: str | None = None
    message: str
    code: str


class ErrorResponse(BaseModel):
    """Standard error response returned by all error handlers.

    Example::

        {
            "error": {
                "code": "not_found",
                "message": "Product with id '123' not found",
                "details": []
            }
        }
    """

    code: str
    message: str
    details: list[ErrorDetail] = []


class ErrorEnvelope(BaseModel):
    """Wrapper to match { "error": { ... } } format."""

    error: ErrorResponse


# ── Pagination


class CursorPaginationParams(BaseModel):
    """Query parameters for cursor-based pagination."""

    cursor: str | None = Field(None, description="Opaque cursor for next page")
    limit: int = Field(20, ge=1, le=100, description="Items per page")


class CursorPaginationMeta(BaseModel):
    """Metadata returned with paginated responses."""

    has_next: bool
    next_cursor: str | None = None


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Paginated collection response with cursor metadata.

    Example::

        {
            "data": [...],
            "meta": {
                "has_next": true,
                "next_cursor": "eyJpZCI6MTQzfQ"
            }
        }
    """

    data: list[DataT]
    meta: CursorPaginationMeta


# ── Health Check


class HealthResponse(BaseModel):
    """Response from the /health endpoint."""

    status: str = "ok"
    version: str
