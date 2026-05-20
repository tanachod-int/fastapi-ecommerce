"""FastAPI application factory and configuration."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import router as v1_router
from app.config import settings
from app.exceptions import (
    AppError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.schemas.common import ErrorEnvelope, ErrorResponse, HealthResponse


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    _register_exception_handlers(app)
    _register_routes(app)
    app.include_router(v1_router)

    return app


# ── Exception Handlers


_EXCEPTION_STATUS_MAP: dict[type[AppError], tuple[int, str]] = {
    NotFoundError: (404, "not_found"),
    ValidationError: (422, "validation_error"),
    AuthenticationError: (401, "authentication_error"),
    AuthorizationError: (403, "authorization_error"),
    ConflictError: (409, "conflict"),
}


def _register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers for all AppError subclasses."""

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        status_code, error_code = _EXCEPTION_STATUS_MAP.get(
            type(exc), (500, "internal_error")
        )
        body = ErrorEnvelope(
            error=ErrorResponse(code=error_code, message=exc.message)
        )
        return JSONResponse(
            status_code=status_code,
            content=body.model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        _request: Request, _exc: Exception
    ) -> JSONResponse:
        body = ErrorEnvelope(
            error=ErrorResponse(
                code="internal_error",
                message="An unexpected error occurred",
            )
        )
        return JSONResponse(status_code=500, content=body.model_dump())


# ── Routes


def _register_routes(app: FastAPI) -> None:
    """Register application routes."""

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    async def health_check() -> HealthResponse:
        """Health check endpoint for load balancers and monitoring."""
        return HealthResponse(
            status="ok",
            version=settings.app_version,
        )


# ── Application Instance

app = create_app()
