"""Generic model execution result container.

This module provides a generic container for model execution results,
supporting both concrete data types and streamable results.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from .status import ResultStatus
from .streamable import StreamableResult

T = TypeVar("T")


class ModelResult(Generic[T]):
    """Generic container for model execution results.

    Wraps execution results with status information and optional metadata.
    Supports both concrete data types and StreamableResult implementations.

    Type Parameters:
        T: The type of data contained in the result

    Attributes:
        status: Execution status (SUCCESS or ERROR)
        data: The result data (can be concrete type or StreamableResult)
        metadata: Optional metadata about the execution

    Examples:
        >>> result = ModelResult(
        ...     status=ResultStatus.SUCCESS,
        ...     data=table_result,
        ...     metadata={"rows": 1000}
        ... )
        >>> if result.status == ResultStatus.SUCCESS:
        ...     for record in result.data:
        ...         process(record)
    """

    def __init__(
        self,
        status: ResultStatus,
        data: StreamableResult,
        metadata: dict | None = None,
    ) -> None:
        """Initialize model result with status and data.

        Args:
            status: The execution status
            data: The result data (concrete type or StreamableResult)
            metadata: Optional metadata dictionary. Defaults to None.
        """
        self._status = status
        self._data = data
        self._metadata = metadata or {}

    @property
    def status(self) -> ResultStatus:
        """Get the execution status.

        Returns:
            The result status (SUCCESS or ERROR)
        """
        return self._status

    @property
    def data(self) -> StreamableResult:
        """Get the result data.

        Returns:
            The wrapped data (concrete type or StreamableResult)
        """
        return self._data

    @property
    def metadata(self) -> dict:
        """Get the execution metadata.

        Returns:
            Dictionary containing execution metadata
        """
        return self._metadata

    @property
    def is_success(self) -> bool:
        """Check if execution was successful.

        Returns:
            True if status is SUCCESS, False otherwise

        Examples:
            >>> if result.is_success:
            ...     process(result.data)
        """
        return self._status == ResultStatus.SUCCESS

    @property
    def is_error(self) -> bool:
        """Check if execution resulted in error.

        Returns:
            True if status is ERROR, False otherwise

        Examples:
            >>> if result.is_error:
            ...     handle_error(result.metadata.get("error"))
        """
        return self._status == ResultStatus.ERROR
