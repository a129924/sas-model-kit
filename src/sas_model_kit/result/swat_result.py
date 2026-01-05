"""SWAT-specific model result implementation.

This module provides a specialized result container for SWAT/CAS operations,
offering convenience methods for common CAS table operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import override

from .cas_table import CASTableResult
from .execution_metadata import ExecutionMetadata
from .model_result import ModelResult

if TYPE_CHECKING:
    from swat import CASTable


class SwatModelResult(ModelResult[CASTableResult]):
    """SWAT-specific model result with CASTable convenience methods.

    Specializes ModelResult for SWAT operations, providing direct access
    to CASTable operations and conversion utilities.

    Examples:
        >>> metadata = ExecutionMetadata(execution_time_ms=150.0, rows_affected=1000)
        >>> result = SwatModelResult.from_table(table, metadata)
        >>> if result.is_success:
        ...     cas_table = result.get_table()
        ...     records = result.to_records()
    """

    @classmethod
    def from_table(
        cls,
        table: CASTable,
        metadata: ExecutionMetadata | None = None,
    ) -> SwatModelResult:
        """Create a successful result from a CASTable.

        Args:
            table: SWAT CASTable instance
            metadata: ExecutionMetadata with timing and row info.
                     If None, defaults to zero timing with rows from table.

        Returns:
            SwatModelResult with SUCCESS status

        Examples:
            >>> table = conn.CASTable("results")
            >>> metadata = ExecutionMetadata(
            ...     execution_time_ms=100.0,
            ...     rows_affected=1000
            ... )
            >>> result = SwatModelResult.from_table(table, metadata)
        """
        from .status import ResultStatus

        # Provide default metadata if not supplied
        if metadata is None:
            metadata = ExecutionMetadata(
                execution_time_ms=0.0,
                rows_affected=0,
            )

        return cls(
            status=ResultStatus.SUCCESS,
            data=CASTableResult(table),
            metadata=metadata,
        )

    @classmethod
    def from_error(
        cls,
        error: str | Exception,
        metadata: ExecutionMetadata | None = None,
    ) -> SwatModelResult:
        """Create an error result.

        Args:
            error: Error message or exception
            metadata: ExecutionMetadata about the failed execution.
                     If None, defaults to zero timing with zero rows.

        Returns:
            SwatModelResult with ERROR status

        Examples:
            >>> metadata = ExecutionMetadata(execution_time_ms=50.0, rows_affected=0)
            >>> result = SwatModelResult.from_error(
            ...     "Table not found",
            ...     metadata=metadata
            ... )
        """
        from .status import ResultStatus

        # Provide default metadata if not supplied
        if metadata is None:
            metadata = ExecutionMetadata(
                execution_time_ms=0.0,
                rows_affected=0,
            )

        return cls(
            status=ResultStatus.ERROR,
            data=None,  # type: ignore[arg-type]
            metadata=metadata,
        )

    @property
    @override
    def data(self) -> CASTableResult:
        """Get the CASTableResult data.

        Returns:
            The wrapped CASTableResult

        Raises:
            RuntimeError: If accessing data on an error result
        """
        if self.is_error:
            msg = "Cannot access data on error result"
            raise RuntimeError(msg)
        return super().data  # type: ignore[return-value]

    def get_table(self) -> CASTable:
        """Get the underlying SWAT CASTable.

        Returns:
            The wrapped CASTable instance

        Raises:
            RuntimeError: If accessing table on an error result

        Examples:
            >>> result = SwatModelResult.from_table(table)
            >>> cas_table = result.get_table()
            >>> print(cas_table.head())
        """
        return self.data.table

    def to_records(self) -> list[dict]:
        """Convert CAS table to list of dictionaries.

        Warning:
            This loads all data into memory. For large tables,
            use stream() on the data object instead.

        Returns:
            List of dictionaries, one per record

        Raises:
            RuntimeError: If accessing data on an error result

        Examples:
            >>> result = SwatModelResult.from_table(table)
            >>> records = result.to_records()
            >>> df = pd.DataFrame(records)
        """
        return self.data.to_records()
