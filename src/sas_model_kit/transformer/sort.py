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

from .exceptions import InvalidColumnError
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
    def execute(self, input_table: CASTable) -> CASTable:
        """Apply sort parameters to table (non-materialized).

        Args:
            input_table: Input CAS table

        Returns:
            New CASTable instance with sort parameters set
            (actual sorting happens at fetch time)

        Raises:
            InvalidColumnError: If any sort column doesn't exist

        Note:
            Returns deepcopy of input table with sort parameters.
            Original table is not modified (inplace=False).
        """
        # Validate columns exist
        missing_cols = [col for col in self.by if col not in input_table.columns]  # type: ignore
        # input_table.columns is pd.Index(...)
        if missing_cols:
            raise InvalidColumnError(
                f"Columns not found in table: {missing_cols}. "
                f"Available columns: {list(input_table.columns)}"  # type: ignore
            )

        # Use CASTable's built-in sort_values (non-materialized)
        sorted_table = input_table.sort_values(
            by=self.by,
            ascending=self.ascending,  # Support single bool or list # type: ignore
            inplace=False,  # Don't modify original
        )

        if sorted_table is None:
            raise RuntimeError("Sorting failed, received None from sort_values()")

        return sorted_table
