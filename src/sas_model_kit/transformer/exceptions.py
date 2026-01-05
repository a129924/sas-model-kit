"""Transformer exceptions.

This module defines exception types for CAS table transformation operations.
All Transformer-layer errors should inherit from TransformationError.

Design Philosophy:
    - TransformationError: Base class for all transformation errors
    - Specific exceptions: For different error scenarios (column, table, etc.)
    - Never swallow exceptions: Let them propagate for proper error handling

Examples:
    >>> raise TransformationError("Transformation failed")
    >>> raise InvalidColumnError("Column 'age' not found")
"""


class TransformationError(Exception):
    """Base exception for transformation operations.

    All Transformer layer errors should inherit from this class.
    This allows catching all transformation-related errors at once.

    Examples:
        >>> try:
        ...     transformer.execute(table)
        ... except TransformationError as e:
        ...     logger.error(f"Transformation failed: {e}")
    """

    pass


class InvalidColumnError(TransformationError):
    """Exception raised when a column name is invalid or not found.

    Examples:
        >>> if column not in table.columns:
        ...     raise InvalidColumnError(f"Column '{column}' not found")
    """

    pass


class TableNotFoundError(TransformationError):
    """Exception raised when a table does not exist.

    Examples:
        >>> if not operation.table_exists(caslib, table):
        ...     raise TableNotFoundError(f"Table {caslib}.{table} not found")
    """

    pass


class ColumnConflictError(TransformationError):
    """Exception raised when a column name conflicts with existing columns.

    Examples:
        >>> if new_column in table.columns:
        ...     raise ColumnConflictError(f"Column '{new_column}' already exists")
    """

    pass
