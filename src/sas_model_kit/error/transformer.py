"""Transformer-related error types."""

from __future__ import annotations

from dataclasses import dataclass, field

from .base import BaseError


@dataclass(frozen=True)
class TransformationFailure(BaseError):
    """Base error for transformation failures."""

    operation: str = ""


@dataclass(frozen=True)
class SortError(TransformationFailure):
    """Sorting failure with a reason.

    This is a semantic/execution error, not a validation error.
    Validation (e.g., column existence) is caller's responsibility.
    """

    reason: str = ""


@dataclass(frozen=True)
class DuplicateKeyError(TransformationFailure):
    """Duplicate key encountered during uniqueness enforcement.

    This is a semantic/execution error, not a validation error.
    Validation (e.g., column existence) is caller's responsibility.
    """

    key_column: str = ""
    duplicate_count: int = 0
