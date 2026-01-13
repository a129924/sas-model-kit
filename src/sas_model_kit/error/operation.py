"""Operation-level error types."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseError


@dataclass(frozen=True)
class OperationError(BaseError):
    """Represents an operation failure."""

    pass


@dataclass(frozen=True)
class TableNotFoundError(OperationError):
    """Raised when a specified table is not found in CAS."""
