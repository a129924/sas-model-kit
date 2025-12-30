"""SWAT-specific model result implementation.

This module provides a specialized result container for SWAT/CAS operations,
offering convenience methods for common CAS table operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import override

from .cas_table import CASTableResult
from .model_result import ModelResult

if TYPE_CHECKING:
    from swat import CASTable


class SwatModelResult(ModelResult[CASTableResult]):
    """SWAT-specific model result with CASTable convenience methods.

    Specializes ModelResult for SWAT operations, providing direct access
    to CASTable operations and conversion utilities.

    Examples:
        >>> result = SwatModelResult.from_table(table)
        >>> if result.is_success:
        ...     cas_table = result.get_table()
        ...     records = result.to_records()
    """

    @classmethod
    def from_table(
        cls,
        table: CASTable,
        metadata: dict | None = None,
    ) -> SwatModelResult:
        """Create a successful result from a CASTable.

        Args:
            table: SWAT CASTable instance
            metadata: Optional metadata dictionary. Defaults to None.

        Returns:
            SwatModelResult with SUCCESS status

        Examples:
            >>> table = conn.CASTable("results")
            >>> result = SwatModelResult.from_table(table)
        """
        from .status import ResultStatus

        return cls(
            status=ResultStatus.SUCCESS,
            data=CASTableResult(table),
            metadata=metadata,
        )

    @classmethod
    def from_error(
        cls,
        error: str | Exception,
        metadata: dict | None = None,
    ) -> SwatModelResult:
        """Create an error result.

        Args:
            error: Error message or exception
            metadata: Optional metadata dictionary. Defaults to None.

        Returns:
            SwatModelResult with ERROR status

        Examples:
            >>> result = SwatModelResult.from_error(
            ...     "Table not found",
            ...     metadata={"table": "missing_table"}
            ... )
        """
        from .status import ResultStatus

        error_msg = str(error) if isinstance(error, Exception) else error
        metadata = metadata or {}
        metadata["error"] = error_msg

        # Create a dummy CASTableResult for type consistency
        # In error cases, data should not be accessed
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
