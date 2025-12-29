"""
Result status enumeration.

This module defines the ResultStatus enum for representing the execution
status of model operations.
"""

from enum import Enum


class ResultStatus(Enum):
    """
    Enumeration of model execution result statuses.

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
