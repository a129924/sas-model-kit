"""CASTable result implementation for SWAT integration.

This module provides a wrapper around SWAT CASTable that implements
the StreamableResult protocol, enabling consistent result handling
across different SAS operation types.
"""

from collections.abc import Iterator
from typing import Any

from typing_extensions import override

from .streamable import StreamableResult

try:
    from swat import CASTable
except ImportError as e:
    raise ImportError(
        "swat package is required for CASTableResult. "
        "Please install it via 'pip install swat'."
    ) from e


class CASTableResult(StreamableResult):
    """Wrapper around SWAT CASTable implementing StreamableResult protocol.

    Provides a consistent interface for accessing CAS table data through
    iteration, streaming, and batch conversion methods.

    Examples:
        >>> table = conn.CASTable("my_table")
        >>> result = CASTableResult(table)
        >>> for record in result:
        ...     print(record)
        >>> records = result.to_records()
    """

    def __init__(self, table: CASTable) -> None:
        """Initialize with a SWAT CASTable instance.

        Args:
            table: SWAT CASTable instance to wrap
        """
        self._table = table

    @property
    def table(self) -> CASTable:
        """Get the underlying SWAT CASTable.

        Returns:
            The wrapped CASTable instance
        """
        return self._table

    @override
    def __iter__(self) -> Iterator[dict]:
        """Iterate over table records one by one.

        Yields:
            Dictionary representation of each record

        Examples:
            >>> result = CASTableResult(table)
            >>> for record in result:
            ...     print(record["id"], record["name"])
        """
        for _, row in self._table.iterrows():  # row type is `pandas.Series`
            yield row.to_dict()

    @override
    def stream(self, batch_size: int = 1000) -> Iterator[list[dict[str, Any]]]:
        """Stream records in batches for memory-efficient processing.

        Uses itertools.islice to efficiently batch rows without append overhead.
        SWAT's internal _fetch(chunksize) handles server-side optimization,
        while islice handles client-side batching for reduced loop iterations.

        Args:
            batch_size: Number of records per batch (default: 1000).
                        Must be > 0.

        Yields:
            List of dictionary records, each batch contains up to batch_size rows.
            Last batch may contain fewer rows.

        Raises:
            ValueError: If batch_size <= 0

        Examples:
            >>> result = CASTableResult(table)
            >>> for batch in result.stream(batch_size=500):
            ...     assert len(batch) <= 500
            ...     process_batch(batch)  # batch is list[dict]
        """
        from itertools import islice

        if batch_size <= 0:
            raise ValueError(f"batch_size must be > 0, got {batch_size}")

        rows_iter = self._table.iterrows()

        while True:
            # Use islice to avoid append overhead
            batch = list(islice(rows_iter, batch_size))

            if not batch:
                break

            # Convert batch of (index, Series) tuples to list[dict]
            yield [row.to_dict() for _, row in batch]

    @override
    def to_records(self) -> list[dict[str, Any]]:
        """Convert entire table to list of dictionaries.

        Warning:
            This loads all data into memory. For large tables,
            consider using stream() instead.

        Returns:
            List of dictionaries, one per record

        Examples:
            >>> result = CASTableResult(table)
            >>> records = result.to_records()
            >>> df = pd.DataFrame(records)
        """
        return self._table.to_dict("records")
