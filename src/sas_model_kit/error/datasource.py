"""Datasource-related error types."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseError


@dataclass(frozen=True)
class UploadFailure(BaseError):
    """Represents a failure during data upload."""

    pass


@dataclass(frozen=True)
class DataFetchFailure(BaseError):
    """Represents a failure during data fetch/download."""

    pass
