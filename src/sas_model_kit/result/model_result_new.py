"""New model result layer using Result[ModelSuccess, ModelError] pattern.

This module provides the refactored ModelResult that follows Rust-style
Result[T, E] semantics. The old ModelResult (with status/data/metadata)
is kept for backward compatibility.

Design:
    - ModelResult is a type alias for Result[ModelSuccess[T], ModelError]
    - ModelSuccess wraps data with ExecutionMetadata
    - ModelError wraps message/metadata with optional exception cause
    - Explicit semantics: Ok/Err instead of status SUCCESS/ERROR
    - Model layer semantics: ExecutionMetadata only on success

Examples:
    >>> # Success case
    >>> success = ModelSuccess(data=table, metadata=ExecutionMetadata(...))
    >>> result: ModelResult[CASTableResult] = Ok(success)
    >>> if result.is_ok:
    ...     data = result.unwrap().data

    >>> # Error case
    >>> error = ModelError(message="...", metadata=ExecutionMetadata(...))
    >>> result: ModelResult[CASTableResult] = Err(error)
    >>> if result.is_err:
    ...     cause = result.unwrap_err().cause
"""

from typing import TypeVar

from .base import Result
from .model_types import ModelError, ModelSuccess

T = TypeVar("T")

# Type alias for model layer semantics: Result[Success[T], Error]
# This represents the new unified interface for all model execution
ModelResult = Result[ModelSuccess[T], ModelError]  # type: ignore

__all__ = ["ModelResult"]
