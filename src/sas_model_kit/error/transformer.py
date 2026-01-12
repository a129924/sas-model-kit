"""Transformer-related error types."""

from __future__ import annotations

from dataclasses import dataclass, field

from .base import BaseError


@dataclass(frozen=True)
class TransformationFailure(BaseError):
    """Base error for transformation failures."""

    operation: str = ""


@dataclass(frozen=True)
class InvalidColumnFailure(TransformationFailure):
    """Missing or invalid required columns."""

    columns: list[str] = field(default_factory=list)
    available_columns: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SortError(TransformationFailure):
    """Sorting failure with a reason."""

    reason: str = ""


@dataclass(frozen=True)
class DuplicateKeyError(TransformationFailure):
    """Duplicate key encountered during uniqueness enforcement."""

    key_column: str = ""
    duplicate_count: int = 0
