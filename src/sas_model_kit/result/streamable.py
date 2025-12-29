"""
Streamable result protocol definition.

This module defines the StreamableResult protocol that all streamable result
implementations must follow (SRP - Single Responsibility Principle).

StreamableResult responsibilities:
- Provide iterator interface for row-by-row processing
- Support batch streaming with configurable batch size
- Allow conversion to list of records for small datasets
- NOT responsible for: Data format conversion (e.g., to DataFrame)
"""

from collections.abc import Iterator
from typing import Protocol, runtime_checkable


@runtime_checkable
class StreamableResult(Protocol):
    """
    Protocol for streamable result implementations.

    All streamable result types (CASTableResult, etc.) must implement this
    interface following the Single Responsibility Principle.

    StreamableResult provides a generic, framework-agnostic interface for
    iterating over result data without forcing conversion to specific formats
    (e.g., pandas DataFrame).

    Methods:
        __iter__(): Row-by-row iteration
        stream(): Batch iteration with configurable size
        to_records(): Convert to list of dictionaries

    Example:
        >>> # Row-by-row iteration (recommended for large datasets)
        >>> for row in result.data:
        ...     process_row(row)
        >>>
        >>> # Batch streaming
        >>> for batch in result.data.stream(batch_size=50000):
        ...     process_batch(batch)
        >>>
        >>> # Convert to records (warning: may cause OOM for large datasets)
        >>> records = result.data.to_records()
        >>> # User decides how to convert:
        >>> # df = pd.DataFrame(records)  # pandas
        >>> # df = pl.DataFrame(records)  # polars
    """

    def __iter__(self) -> Iterator[dict]:
        """
        Iterate over result rows one by one.

        This method enables row-by-row iteration over the result data,
        which is memory-efficient for large datasets.

        Yields:
            dict: Each row as a dictionary with column names as keys

        Example:
            >>> for row in result.data:
            ...     print(row['score'])
        """
        ...

    def stream(self, batch_size: int = 1000) -> Iterator[dict]:
        """
        Stream result data in batches.

        This method provides batch iteration with configurable batch size,
        allowing developers to balance memory usage and performance.

        Args:
            batch_size: Number of rows per batch (default: 1000)

        Yields:
            dict: Each row as a dictionary

        Example:
            >>> # Process in batches of 50,000 rows
            >>> for row in result.data.stream(batch_size=50000):
            ...     process_row(row)
        """
        ...

    def to_records(self) -> list[dict]:
        """
        Convert all result data to a list of dictionaries.

        Warning:
            This method loads all data into memory at once. For large datasets
            (millions of rows), this may cause Out-Of-Memory (OOM) errors.
            Use stream() or __iter__() instead for large datasets.

        Returns:
            list[dict]: All rows as a list of dictionaries

        Raises:
            MemoryError: If dataset is too large to fit in memory

        Example:
            >>> # Only for small datasets
            >>> records = result.data.to_records()
            >>> # Convert to desired format:
            >>> import pandas as pd
            >>> df = pd.DataFrame(records)
        """
        ...
