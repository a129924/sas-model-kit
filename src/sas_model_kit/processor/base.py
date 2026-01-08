"""Batch processor contracts.

This module defines the abstract base classes and error types for
batch processing in the package. Classes here must follow CSRP and
act as clear contracts for concrete processors.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Final, Generic, TypeVar

from sas_model_kit.operation import OperationProtocol
from sas_model_kit.result import Err, Ok, Result

ExecutionItemType = TypeVar("ExecutionItemType")  # Generic execution result type
ResourceT = TypeVar("ResourceT")  # Operation input type (DataFrame, SASDataFrame, etc.)
UploadReturnT = TypeVar(
    "UploadReturnT"
)  # Operation.upload_data() return type (CASTable, etc.)
BatchReturnT = TypeVar(
    "BatchReturnT"
)  # process_batch() return type (dict[str, str], etc.)


@dataclass(frozen=True)
class ProcessorError(Generic[BatchReturnT]):
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
    partial_output: BatchReturnT | None = None


@dataclass(frozen=True)
class ExecutionSuccess(Generic[ExecutionItemType]):
    """Successful execution result (CSRP: immutable data carrier).

    Attributes:
        id: The ID processed
        data: Execution result data (e.g., CASTable for SWAT, str for path, etc.)
    """

    id: str | int
    data: ExecutionItemType


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
# Note: In concrete implementations (e.g., SWAT), ExecutionItemType will be CASTable
ExecutionItem = ExecutionSuccess[ExecutionItemType] | ExecutionError


ProcessorResult = Result[BatchReturnT, ProcessorError]


class BaseBatchProcessor(ABC, Generic[ResourceT, UploadReturnT, BatchReturnT]):
    """Abstract base class for batch processors (CSRP).

    Generic parameters:
        ResourceT: Operation input type (e.g., DataFrame, SASDataFrame)
        UploadReturnT: Operation.upload_data() return type (e.g., CASTable)
        BatchReturnT: process_batch() return type (e.g., dict[str, str])

    Responsibilities (CSRP):
    - Define a single abstract method for processing a batch
    - Provide helper methods for success/error wrapping
    """

    operation: OperationProtocol[ResourceT, UploadReturnT]

    def __init__(self, operation: OperationProtocol[ResourceT, UploadReturnT]) -> None:
        self.operation: Final[OperationProtocol[ResourceT, UploadReturnT]] = operation

    @abstractmethod
    def process_batch(self, *args: Any, **kwargs: Any) -> ProcessorResult[BatchReturnT]:
        """Process a batch of inputs and return a domain result."""
        ...

    # Utilities
    def _ok(self, value: BatchReturnT) -> ProcessorResult[BatchReturnT]:
        return Ok(value)

    def _err(
        self,
        message: str,
        *,
        errors: list[dict[str, Any]] | None = None,
        cause: Exception | None = None,
        partial_output: BatchReturnT | None = None,
    ) -> ProcessorResult[BatchReturnT]:
        return Err(
            ProcessorError(
                message=message,
                errors=errors,
                cause=cause,
                partial_output=partial_output,
            )
        )
