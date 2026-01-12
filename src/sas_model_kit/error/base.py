"""Error base classes and protocol for SAS Model Kit.

Provides a lightweight, serializable error hierarchy that avoids inheriting
from Exception. Errors are dataclasses that carry code, message, severity,
optional cause, and context for diagnostics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, runtime_checkable


class ErrorSeverity(Enum):
    """Severity levels for errors."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@runtime_checkable
class ErrorProtocol(Protocol):
    """Explicit contract that all error objects must follow."""

    code: str
    message: str
    severity: ErrorSeverity
    context: dict[str, Any]
    cause: Exception | None

    def to_dict(self) -> dict[str, Any]:
        """Serialize the error into a dict representation."""
        ...

    def print_debug_info(self) -> None:
        """Print debugging information, including traceback if present."""
        ...


@dataclass(frozen=True)
class BaseError(ErrorProtocol):
    """Base class for all errors (non-Exception dataclass)."""

    code: str
    message: str
    severity: ErrorSeverity = ErrorSeverity.ERROR
    cause: Exception | None = field(default=None, repr=False, compare=False)
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-friendly dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "context": self.context,
        }

    def print_debug_info(self) -> None:
        """Print traceback for the underlying cause if present."""
        if self.cause:
            import traceback

            traceback.print_exception(
                type(self.cause),
                self.cause,
                self.cause.__traceback__,
            )
