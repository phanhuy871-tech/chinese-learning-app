class AppError(Exception):
    """Base exception for expected application errors."""


class DataSyncError(AppError):
    """Raised when a data source cannot be read or parsed."""


class NotEnoughDataError(AppError):
    """Raised when a game cannot build enough answer options."""

