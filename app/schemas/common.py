"""Shared schemas used across the application."""

from pydantic import BaseModel, Field


# ── Error Response ──────────────────────────────────────────────


class ErrorDetail(BaseModel):
    """Single field-level validation error."""

    field: str | None = None
    message: str
    code: str


class ErrorResponse(BaseModel):
    """Standard error response returned by all error handlers.

    Example:
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


# ── Pagination ──────────────────────────────────────────────────


class CursorPaginationParams(BaseModel):
    """Query parameters for cursor-based pagination."""

    cursor: str | None = Field(None, description="Opaque cursor for next page")
    limit: int = Field(20, ge=1, le=100, description="Items per page")


class CursorPaginationMeta(BaseModel):
    """Metadata returned with paginated responses."""

    has_next: bool
    next_cursor: str | None = None


# ── Health Check ────────────────────────────────────────────────


class HealthResponse(BaseModel):
    """Response from the /health endpoint."""

    status: str = "ok"
    version: str
