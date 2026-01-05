"""Model result types for Result[T, E] pattern.

This module provides the success and error types for ModelResult,
following the Rust-style Result[T, E] pattern with explicit semantics.

Types:
    - ModelSuccess[T]: Wraps successful execution data with metadata
    - ModelError: Wraps error information with cause chain

Design:
    - Frozen dataclasses for immutability
    - ModelSuccess is generic over result type T
    - ModelError includes optional exception cause for debugging
    - ExecutionMetadata only on success (Model layer semantics)

Examples:
    >>> # Success case
    >>> success = ModelSuccess(
    ...     data=table_result,
    ...     metadata=ExecutionMetadata(execution_time_ms=150.0)
    ... )
    >>> result = Ok[ModelSuccess](success)

    >>> # Error case
    >>> error = ModelError(
    ...     message="Transformation failed",
    ...     metadata=ExecutionMetadata(execution_time_ms=50.0),
    ...     cause=ValueError("Invalid column")
    ... )
    >>> result = Err[ModelError](error)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from .execution_metadata import ExecutionMetadata

T = TypeVar("T")


@dataclass(frozen=True)
class ModelSuccess(Generic[T]):
    """Successful model execution result with metadata.

    Wraps the successful result data along with execution metadata.
    Only created when execution completes successfully.

    Type Parameters:
        T: Type of the result data (e.g., CASTableResult, None)

    Attributes:
        data: The result data (can be None for models with no output)
        metadata: ExecutionMetadata with timing and resource info

    Examples:
        >>> success = ModelSuccess(
        ...     data=table_result,
        ...     metadata=ExecutionMetadata(execution_time_ms=150.0)
        ... )
    """

    data: T | None
    metadata: ExecutionMetadata


@dataclass(frozen=True)
class ModelError:
    """Failed model execution error information.

    Wraps error information including metadata about the failed execution.
    Optionally includes the underlying exception cause for debugging.

    Attributes:
        message: Human-readable error message
        metadata: ExecutionMetadata about the failed execution
        cause: Optional underlying exception (for cause chain)

    Examples:
        >>> error = ModelError(
        ...     message="Failed to process table",
        ...     metadata=ExecutionMetadata(execution_time_ms=50.0),
        ...     cause=ValueError("Invalid column")
        ... )
    """

    message: str
    metadata: ExecutionMetadata
    cause: Exception | None = None
