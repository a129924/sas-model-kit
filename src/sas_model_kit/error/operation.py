"""Operation-level error types."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseError


@dataclass(frozen=True)
class OperationError(BaseError):
    """Represents an operation failure."""

    pass
