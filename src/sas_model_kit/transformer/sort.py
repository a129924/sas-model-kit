"""CAS Table Sort Transformer (non-materialized).

This module implements sorting for CAS tables using CASTable.sort_values().
Unlike materialized sorting, this transformer only sets sort parameters and
doesn't create a new CAS table. The actual sorting happens at fetch time.

Design Decision (Plan @a129924):
    - Non-materialized: Uses CASTable.sort_values() which embeds sort parameters
    - Zero resource overhead: No new CAS table created
    - Suitable for: Query-time sorting
    - Returns: A CASTable with embedded sort parameters

Examples:
    >>> # Single column ascending
    >>> transformer = SortTransformer(operation, by=['age'])
    >>> sorted_table = transformer.execute(table)

    >>> # Multi-column mixed sort
    >>> transformer = SortTransformer(
    ...     operation,
    ...     by=['region', 'sales'],
    ...     ascending=[True, False]  # region asc, sales desc
    ... )
    >>> sorted_table = transformer.execute(table)
"""

try:
    from swat import CASTable
except ImportError as e:
    raise ImportError(
        "swat package is required for SortTransformer. "
        "Please install it via 'pip install swat'."
    ) from e

from typing_extensions import override

from sas_model_kit.error import OperationError, SortError
from sas_model_kit.result import Err, Ok, SortExecutionResult

from .protocol import CASTableTransformer


class SortTransformer(CASTableTransformer):
    """CAS Table Sort Transformer (non-materialized).

    Applies sort order to a CAS table by setting sort parameters.
    Does not materialize a new table - the sorting happens at fetch time.

    Attributes:
        by: Column names to sort by
        ascending: Sort order (True=ascending, False=descending)

    Examples:
        >>> # Single column
        >>> transformer = SortTransformer(operation, by=['age'])
        >>> result = transformer.execute(table)

        >>> # Multiple columns with mixed order
        >>> transformer = SortTransformer(
        ...     operation,
        ...     by=['region', 'sales'],
        ...     ascending=[True, False]
        ... )
        >>> result = transformer.execute(table)
    """

    def __init__(
        self, operation, by: list[str], ascending: bool | list[bool] = True
    ) -> None:
        """Initialize sort transformer.

        Args:
            operation: Operation protocol instance
            by: Column names to sort by
            ascending: Sort direction (single bool or list of bools)

        Raises:
            ValueError: If by is empty or ascending list length doesn't match by

        Examples:
            >>> transformer = SortTransformer(op, by=['col1', 'col2'])
            >>> transformer = SortTransformer(
            ...     op,
            ...     by=['a', 'b', 'c'],
            ...     ascending=[True, False, True]
            ... )
        """
        super().__init__(operation)

        if not by:
            raise ValueError("Sort by columns cannot be empty")

        if isinstance(ascending, list) and len(ascending) != len(by):
            raise ValueError(
                f"Length of ascending ({len(ascending)}) must match "
                f"length of by ({len(by)})"
            )

        self.by = by
        self.ascending = ascending

    @override
    def execute(self, input_table: CASTable) -> SortExecutionResult:
        """Apply sort parameters to table (non-materialized).

        Pure Transform: Only executes sorting, assumes input is valid.
        Validation (e.g., column existence) is caller's responsibility.

        Args:
            input_table: Input CAS table (caller must ensure columns exist)

        Returns:
            New CASTable instance with sort parameters set
            (actual sorting happens at fetch time)

        Note:
            Returns deepcopy of input table with sort parameters.
            Original table is not modified (inplace=False).
        """
        try:
            sorted_table = input_table.sort_values(
                by=self.by,
                ascending=self.ascending,  # type: ignore
                inplace=False,
            )
        except Exception as exc:
            return Err(
                OperationError(
                    code="SORT_UNEXPECTED_EXCEPTION",
                    message=str(exc),
                    cause=exc,
                    context={"exception_type": type(exc).__name__},
                )
            )

        if sorted_table is None:
            return Err(
                SortError(
                    code="SORT_RETURNED_NONE",
                    message="Sorting failed, received None from sort_values()",
                    reason="sort_values returned None",
                )
            )

        return Ok(sorted_table)
