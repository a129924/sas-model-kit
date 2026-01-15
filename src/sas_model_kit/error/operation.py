"""Operation-level error types for SWAT operations.

This module provides type-safe error handling for SWAT operations with:
- OperationErrorCode: Enum for error classification (supports match/case)
- OperationError: Manual Exception implementation with proper error chaining
- TableNotFoundError: Named error for ValidateAble Protocol

Design decisions:
- NOT using @dataclass (incompatible with Exception inheritance)
- Manual __init__ properly calls super().__init__(code.value, message)
- Supports pickle serialization for multi-process/logging systems
- Auto-sets __cause__ for error chain preservation
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional


class OperationErrorCode(Enum):
    """Type-safe error codes for SWAT operation failures.

    Using Enum provides:
    - Type safety and IDE autocomplete
    - match/case pattern matching support
    - Clear error categorization
    """

    # Action-related errors
    ACTION_SET_NOT_FOUND = "ACTION_SET_NOT_FOUND"
    ACTION_NOT_FOUND = "ACTION_NOT_FOUND"

    # Execution errors
    SWAT_EXECUTION_ERROR = "SWAT_EXECUTION_ERROR"

    # Table-related errors (Note: TableNotFoundError is a named class)
    TABLE_NOT_FOUND = "TABLE_NOT_FOUND"

    # Operation-specific errors
    READ_FAILED = "READ_FAILED"
    WRITE_FAILED = "WRITE_FAILED"
    SORT_FAILED = "SORT_FAILED"
    PARSE_FAILED = "PARSE_FAILED"

    # Generic
    UNKNOWN = "UNKNOWN"


class OperationError(Exception):
    """SWAT operation failure error.

    Manual implementation (NOT using @dataclass) to ensure proper Exception
    inheritance and pickle support.

    Args:
        code: Error code enum for classification
        message: Human-readable error message
        cause: Optional underlying exception (auto-sets __cause__)

    Examples:
        >>> # Basic usage
        >>> err = OperationError(
        ...     code=OperationErrorCode.READ_FAILED,
        ...     message="Failed to read table",
        ...     cause=some_exception
        ... )

        >>> # Match/case pattern
        >>> match result:
        ...     case Err(error=OperationError(code=OperationErrorCode.ACTION_SET_NOT_FOUND)):
        ...         print("Need to load actionset")
        ...     case Err(error=OperationError(code=OperationErrorCode.SWAT_EXECUTION_ERROR)):
        ...         print("SWAT execution failed")
    """

    def __init__(
        self,
        code: OperationErrorCode,
        message: str,
        *,
        cause: Optional[Exception] = None,
    ) -> None:
        self.code = code
        self.message = message
        self.cause = cause

        # ✅ Properly set Exception.args for serialization
        super().__init__(code.value, message)

        # Auto-set __cause__ to preserve error chain (for debugging)
        if cause is not None:
            self.__cause__ = cause

    def __str__(self) -> str:
        """String representation showing code and message."""
        return f"[{self.code.value}] {self.message}"

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        cause_repr = f", cause={self.cause!r}" if self.cause else ""
        return (
            f"OperationError(code={self.code!r}, message={self.message!r}{cause_repr})"
        )

    # Pickle support (for multi-process/logging systems)
    def __reduce__(
        self,
    ) -> tuple[type[OperationError], tuple[OperationErrorCode, str], dict[str, Any]]:
        """Enable pickle serialization."""
        return (self.__class__, (self.code, self.message), {"cause": self.cause})

    def __setstate__(self, state: dict[str, Any]) -> None:
        """Restore state from pickle."""
        self.cause = state.get("cause")
        if self.cause is not None:
            self.__cause__ = self.cause


class TableNotFoundError(OperationError):
    """Table not found error (named error for ValidateAble Protocol).

    This is a named error class because:
    - Used in ValidateAble.ensure_exists() signature
    - Callers need isinstance() check for special business logic
    - Indicates a recoverable condition (table creation needed)

    Examples:
        >>> # Raise in ValidateAble implementation
        >>> if not library_table.exists():
        ...     raise TableNotFoundError(
        ...         message=f"Table {caslib}.{table} not found",
        ...         cause=None
        ...     )

        >>> # Catch in caller
        >>> try:
        ...     result = validatable.ensure_exists(library_table)
        ... except TableNotFoundError as e:
        ...     # Handle missing table (e.g., create it)
        ...     pass
    """

    def __init__(self, message: str, *, cause: Optional[Exception] = None) -> None:
        super().__init__(OperationErrorCode.TABLE_NOT_FOUND, message, cause=cause)

    # Override __reduce__ for pickle support with correct signature
    def __reduce__(self) -> tuple[type[TableNotFoundError], tuple[str], dict[str, Any]]:
        """Enable pickle serialization for TableNotFoundError."""
        return (self.__class__, (self.message,), {"cause": self.cause})
