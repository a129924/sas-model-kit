"""Parameter validation error types."""

from __future__ import annotations

from dataclasses import dataclass, field

from .base import BaseError


@dataclass(frozen=True)
class ValidationFailure(BaseError):
    """Base class for parameter validation failures."""

    field_name: str = ""


@dataclass(frozen=True)
class MissingFieldFailure(ValidationFailure):
    """Required field is missing."""

    pass


@dataclass(frozen=True)
class InvalidTypeFailure(ValidationFailure):
    """Field has invalid type."""

    expected_type: str = ""
    actual_type: str = ""


@dataclass(frozen=True)
class ConflictingRuleFailure(ValidationFailure):
    """Business rules conflict between fields."""

    conflicting_fields: list[str] = field(default_factory=list)
