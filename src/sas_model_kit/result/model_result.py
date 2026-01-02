"""Generic model execution result container.

This module provides a generic container for model execution results,
supporting both concrete data types and streamable results with proper metadata tracking.

Design:
    - data: Optional (some models don't produce CASTable output)
    - metadata: ExecutionMetadata (no duplicate output_* fields)
    - Supports both synchronous results and StreamableResult implementations
"""

from __future__ import annotations

from typing import Generic, TypeVar

from .execution_metadata import ExecutionMetadata
from .status import ResultStatus
from .streamable import StreamableResult

T = TypeVar("T")


class ModelResult(Generic[T]):
    """Generic container for model execution results.

    Wraps execution results with status information and execution metadata.
    Supports both concrete data types and StreamableResult implementations.
    Data is optional to support models that don't produce output tables.

    Type Parameters:
        T: The type of data contained in the result (e.g., CASTableResult)

    Attributes:
        status: Execution status (SUCCESS or ERROR)
        data: Optional result data. None for models that don't produce output.
        metadata: Execution metadata (time, rows, etc.). No duplicate output info.

    Examples:
        >>> # With CASTable output
        >>> result = ModelResult(
        ...     status=ResultStatus.SUCCESS,
        ...     data=table_result,
        ...     metadata=ExecutionMetadata(
        ...         execution_time_ms=150.0,
        ...         rows_affected=1000,
        ...     )
        ... )
        >>> if result.is_success and result.data:
        ...     print(f"Output at {result.data.caslib}.{result.data.name}")

        >>> # Without data output (e.g., explanation metadata only)
        >>> result_no_data = ModelResult(
        ...     status=ResultStatus.SUCCESS,
        ...     data=None,
        ...     metadata=ExecutionMetadata(
        ...         execution_time_ms=250.0,
        ...         rows_affected=0,
        ...         intended_output_caslib="models",
        ...         intended_output_table="explain_results",
        ...     )
        ... )
    """

    def __init__(
        self,
        status: ResultStatus,
        data: StreamableResult | None,
        metadata: ExecutionMetadata,
    ) -> None:
        """Initialize model result with status, optional data, and metadata.

        Args:
            status: The execution status
            data: Optional result data (None for models that don't produce output)
            metadata: Execution metadata with timing and row information

        Raises:
            TypeError: If metadata is not ExecutionMetadata
        """
        if not isinstance(metadata, ExecutionMetadata):
            msg = f"metadata must be ExecutionMetadata, got {type(metadata)}"
            raise TypeError(msg)

        self._status = status
        self._data = data
        self._metadata = metadata

    @property
    def status(self) -> ResultStatus:
        """Get the execution status.

        Returns:
            The result status (SUCCESS or ERROR)
        """
        return self._status

    @property
    def data(self) -> StreamableResult | None:
        """Get the optional result data.

        Returns:
            The wrapped data (can be None if no output was produced)
        """
        return self._data

    @property
    def metadata(self) -> ExecutionMetadata:
        """Get the execution metadata.

        Returns:
            ExecutionMetadata with timing and row information
        """
        return self._metadata

    @property
    def is_success(self) -> bool:
        """Check if execution was successful.

        Returns:
            True if status is SUCCESS, False otherwise

        Examples:
            >>> if result.is_success:
            ...     if result.data:
            ...         process(result.data)
            ...     else:
            ...         use_metadata_info(result.metadata)
        """
        return self._status == ResultStatus.SUCCESS

    @property
    def is_error(self) -> bool:
        """Check if execution resulted in error.

        Returns:
            True if status is ERROR, False otherwise
        """
        return self._status == ResultStatus.ERROR
