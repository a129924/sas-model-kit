"""Data-level error types for non-operation failures."""

from __future__ import annotations

from enum import Enum
from typing import Any

from typing_extensions import override


class DataErrorCode(Enum):
    """Type-safe error codes for data-related failures."""

    COLUMN_NOT_FOUND = "COLUMN_NOT_FOUND"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"
    DATA_TYPE_MISMATCH = "DATA_TYPE_MISMATCH"
    INVALID_DATA = "INVALID_DATA"
    UNKNOWN = "UNKNOWN"


class DataError(Exception):
    """Data-related failure error.

    Args:
        code: Error code enum for classification
        message: Human-readable error message
        cause: Optional underlying exception (auto-sets __cause__)
    """

    def __init__(
        self,
        code: DataErrorCode,
        message: str,
        *,
        cause: Exception | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.cause = cause

        super().__init__(code.value, message)

        if cause is not None:
            self.__cause__ = cause

    def __str__(self) -> str:
        return f"[{self.code.value}] {self.message}"

    def __repr__(self) -> str:
        cause_repr = f", cause={self.cause!r}" if self.cause else ""
        return f"DataError(code={self.code!r}, message={self.message!r}{cause_repr})"

    def __reduce__(
        self,
    ) -> tuple[type[DataError], tuple[DataErrorCode, str], dict[str, Any]]:
        return (self.__class__, (self.code, self.message), {"cause": self.cause})

    @override
    def __setstate__(self, state: dict[str, Any] | None) -> None:
        self.cause = state.get("cause") if state is not None else None
        if self.cause is not None:
            self.__cause__ = self.cause


class ColumnNotFoundError(DataError):
    """Column not found in input data."""

    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(DataErrorCode.COLUMN_NOT_FOUND, message, cause=cause)

    def __reduce__(
        self,
    ) -> tuple[type[ColumnNotFoundError], tuple[str], dict[str, Any]]:
        return (self.__class__, (self.message,), {"cause": self.cause})


class SchemaMismatchError(DataError):
    """Schema mismatch between input tables or data sources."""

    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(DataErrorCode.SCHEMA_MISMATCH, message, cause=cause)

    def __reduce__(
        self,
    ) -> tuple[type[SchemaMismatchError], tuple[str], dict[str, Any]]:
        return (self.__class__, (self.message,), {"cause": self.cause})


class DataTypeMismatchError(DataError):
    """Data type mismatch in input values."""

    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(DataErrorCode.DATA_TYPE_MISMATCH, message, cause=cause)

    def __reduce__(
        self,
    ) -> tuple[type[DataTypeMismatchError], tuple[str], dict[str, Any]]:
        return (self.__class__, (self.message,), {"cause": self.cause})


class InvalidDataError(DataError):
    """Generic invalid data error."""

    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(DataErrorCode.INVALID_DATA, message, cause=cause)

    def __reduce__(
        self,
    ) -> tuple[type[InvalidDataError], tuple[str], dict[str, Any]]:
        return (self.__class__, (self.message,), {"cause": self.cause})


__all__ = [
    "DataErrorCode",
    "DataError",
    "ColumnNotFoundError",
    "SchemaMismatchError",
    "DataTypeMismatchError",
    "InvalidDataError",
]
