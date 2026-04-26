"""Custom exception hierarchy for the application.

All exceptions inherit from AppError so they can be caught
by a single exception handler in main.py.
"""


class AppError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str = "An unexpected error occurred"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str = "Resource", resource_id: str = ""):
        detail = f"{resource} not found"
        if resource_id:
            detail = f"{resource} with id '{resource_id}' not found"
        super().__init__(message=detail)


class ValidationError(AppError):
    """Raised when input validation fails at the service layer."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message=message)


class AuthenticationError(AppError):
    """Raised when authentication fails (invalid credentials or token)."""

    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(message=message)


class AuthorizationError(AppError):
    """Raised when user lacks permission for the requested action."""

    def __init__(self, message: str = "Not enough permissions"):
        super().__init__(message=message)


class ConflictError(AppError):
    """Raised when a resource already exists (e.g. duplicate email)."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message=message)
