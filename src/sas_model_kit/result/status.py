"""
Result status enumeration.

This module defines the ResultStatus enum for representing the execution
status of model operations.

DEPRECATED:
    ResultStatus will be replaced by Result[ModelSuccess[T], ModelError] pattern
    following Rust-style semantics. Use Ok/Err variants instead of SUCCESS/ERROR.

    Old approach:
        result = ModelResult(status=ResultStatus.SUCCESS, data=..., metadata=...)

    New approach:
        result = Ok[ModelSuccess](ModelSuccess(data=..., metadata=...))
        or
        result = Err[ModelError](ModelError(message=..., metadata=...))
"""

from enum import Enum

from typing_extensions import deprecated


# DEPRECATED: Use Result[ModelSuccess[T], ModelError] instead.
@deprecated(
    "ResultStatus is deprecated. Use Result[ModelSuccess[T], ModelError] instead."
)
class ResultStatus(Enum):
    """
    Enumeration of model execution result statuses.

    DEPRECATED: Use Result[ModelSuccess[T], ModelError] instead.

    Attributes:
        SUCCESS: Execution completed successfully (may have warnings)
        ERROR: Execution failed

    Example:
        >>> result = model.execute(param, operation)
        >>> if result.status == ResultStatus.SUCCESS:
        ...     print("Execution successful")
        >>> else:
        ...     print(f"Execution failed: {result.errors}")
    """

    SUCCESS = "success"
    ERROR = "error"
