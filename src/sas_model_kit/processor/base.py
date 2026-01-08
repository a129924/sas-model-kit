"""Batch processor contracts.

This module defines the abstract base classes and error types for
batch processing in the package. Classes here must follow CSRP and
act as clear contracts for concrete processors.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, Union

from swat import CASTable

from sas_model_kit.operation import OperationProtocol
from sas_model_kit.result import Err, Ok, Result

T = TypeVar("T")


@dataclass(frozen=True)
class ProcessorError:
    """Represents an error occurred during batch processing.

    Attributes:
        message: Error message
        errors: List of individual errors (per-ID failures)
        cause: Underlying exception (if any)
        partial_output: Output from partially successful batch (if any)
                       Set when some IDs succeeded but others failed

    Examples:
        >>> # All failed: no partial_output
        >>> err = ProcessorError(
        ...     message="All IDs failed",
        ...     errors=[{"id": 1, "message": "..."}],
        ... )

        >>> # Partial success: partial_output set
        >>> err = ProcessorError(
        ...     message="Batch completed with partial errors",
        ...     errors=[{"id": 2, "message": "..."}],
        ...     partial_output={"caslib": "public", "name": "results"},
        ... )
    """

    message: str
    errors: list[dict[str, Any]] | None = None
    cause: Exception | None = None
    partial_output: dict[str, str] | None = None


@dataclass(frozen=True)
class ExecutionSuccess:
    """Successful execution result (CSRP: immutable data carrier).

    Attributes:
        id: The ID processed
        cas_table: CASTable reference from successful upload
    """

    id: str | int
    cas_table: CASTable


@dataclass(frozen=True)
class ExecutionError:
    """Failed execution result (CSRP: immutable data carrier).

    Attributes:
        id: The ID that failed
        message: Error message
    """

    id: str | int
    message: str


# Union type for execution results
ExecutionItem = ExecutionSuccess | ExecutionError


ProcessorResult = Result[T, ProcessorError]


class BaseBatchProcessor(ABC, Generic[T]):
    """Abstract base class for batch processors (CSRP).

    Responsibilities (CSRP):
    - Define a single abstract method for processing a batch
    - Provide helper methods for success/error wrapping
    """

    operation: OperationProtocol

    def __init__(self, operation: OperationProtocol) -> None:
        self.operation = operation

    @abstractmethod
    def process_batch(self, *args: Any, **kwargs: Any) -> ProcessorResult[T]:
        """Process a batch of inputs and return a domain result."""
        ...

    # Utilities
    def _ok(self, value: T) -> ProcessorResult[T]:
        return Ok(value)

    def _err(
        self,
        message: str,
        *,
        errors: list[dict[str, Any]] | None = None,
        cause: Exception | None = None,
        partial_output: Any | None = None,
    ) -> ProcessorResult[T]:
        return Err(
            ProcessorError(
                message=message,
                errors=errors,
                cause=cause,
                partial_output=partial_output,
            )
        )
