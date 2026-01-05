"""CAS Table Unique Key Transformer (materialized).

This module implements adding a unique ID column to CAS tables using
SAS DATA steps. This creates a new CAS table with the unique key column.

Design Decision (Plan @a129924):
    - Materialized: Executes DATA step to create new table
    - Distributed-safe: Uses _threadid_ * 1e9 + _N_ for true uniqueness in CAS
    - Creates new table: Data is stored on CAS server
    - Suitable for: Operations requiring permanent unique identifiers

Examples:
    >>> # Default column name "_id"
    >>> transformer = AddUniqueKeyTransformer(operation)
    >>> result_table = transformer.execute(table)

    >>> # Custom column name and output location
    >>> transformer = AddUniqueKeyTransformer(
    ...     operation,
    ...     column_name="row_id",
    ...     output_table="my_table_with_id"
    ... )
    >>> result_table = transformer.execute(table)
"""

import time

try:
    from swat import CASTable
except ImportError as e:
    raise ImportError(
        "swat package is required for AddUniqueKeyTransformer. "
        "Please install it via 'pip install swat'."
    ) from e

from typing_extensions import override

from .exceptions import ColumnConflictError, TransformationError
from .protocol import CASTableTransformer


class AddUniqueKeyTransformer(CASTableTransformer):
    """Add unique key column to CAS table (materialized).

    Creates a new CAS table with an additional unique ID column.
    Uses SAS DATA step to ensure distributed safety in CAS.

    The unique key is computed as: _threadid_ * 1000000000 + _N_
    This ensures uniqueness across all threads in distributed CAS.

    Attributes:
        column_name: Name of the unique key column
        output_caslib: Output CAS library (None uses input table's caslib)
        output_table: Output table name (None auto-generates timestamp-based name)

    Examples:
        >>> # Default settings
        >>> transformer = AddUniqueKeyTransformer(operation)
        >>> result = transformer.execute(table)

        >>> # Custom output location
        >>> transformer = AddUniqueKeyTransformer(
        ...     operation,
        ...     column_name="pk",
        ...     output_table="results_with_pk"
        ... )
        >>> result = transformer.execute(table)
    """

    def __init__(
        self,
        operation,
        column_name: str = "_id",
        output_caslib: str | None = None,
        output_table: str | None = None,
    ) -> None:
        """Initialize unique key transformer.

        Args:
            operation: Operation protocol instance
            column_name: Name for the unique key column (default "_id")
            output_caslib: Output library (None uses input table's caslib)
            output_table: Output table name (None auto-generates)

        Raises:
            ValueError: If column_name is invalid

        Examples:
            >>> transformer = AddUniqueKeyTransformer(operation)
            >>> transformer = AddUniqueKeyTransformer(
            ...     operation,
            ...     column_name="unique_id",
            ...     output_table="new_table"
            ... )
        """
        super().__init__(operation)

        # Validate column name
        if not column_name or not column_name.replace("_", "").isalnum():
            raise ValueError(
                f"Invalid column_name: '{column_name}'. "
                f"Must be alphanumeric with underscores only."
            )

        self.column_name = column_name
        self.output_caslib = output_caslib
        self.output_table = output_table

    @override
    def execute(self, input_table: CASTable) -> CASTable:
        """Add unique key column and create new CAS table.

        Args:
            input_table: Input CAS table

        Returns:
            New CASTable with unique key column

        Raises:
            ColumnConflictError: If column name already exists
            TransformationError: If DATA step execution fails

        Note:
            Creates a new table on the CAS server.
            The unique key uses _threadid_ * 1e9 + _N_ for distributed safety.
        """
        # Check for column name conflict
        if self.column_name in input_table.columns:  # type: ignore # input_table.columns is pd.Index(...)
            raise ColumnConflictError(
                f"Column '{self.column_name}' already exists in table. "
                f"Choose a different column name."
            )

        # Determine output location
        input_caslib = input_table.params.get("caslib", "public")
        output_caslib = self.output_caslib or input_caslib

        # Generate output table name if not provided
        if self.output_table:
            output_table = self.output_table
        else:
            timestamp = int(time.time() * 1000)
            input_name = input_table.params["name"]
            output_table = f"{input_name}_with_{self.column_name}_{timestamp}"

        # Generate DATA step code
        code = self._generate_data_step_code(
            input_table, input_caslib, output_caslib, output_table
        )

        # Execute DATA step
        try:
            result = self.operation.call_action(
                "datastep.runcode", code=code, _messagelevel="error"
            )
        except Exception as e:
            raise TransformationError(f"Failed to add unique key column: {e}") from e

        # Check execution status
        if hasattr(result, "status") and result.status:
            raise TransformationError(f"DATA step failed with status: {result.status}")

        # Return new table
        connection = input_table.get_connection()
        output_cas_table = connection.CASTable(name=output_table, caslib=output_caslib)

        return output_cas_table

    def _generate_data_step_code(
        self,
        input_table: CASTable,
        input_caslib: str,
        output_caslib: str,
        output_table: str,
    ) -> str:
        """Generate SAS DATA step code.

        Creates a DATA step that:
        1. Reads from input table
        2. Adds unique key column
        3. Writes to output table

        The unique key formula: _threadid_ * 1000000000 + _N_
        This ensures uniqueness across distributed CAS execution.

        Args:
            input_table: Input CAS table
            input_caslib: Input CAS library name
            output_caslib: Output CAS library name
            output_table: Output table name

        Returns:
            SAS DATA step code string
        """
        input_name = input_table.params["name"]

        code = f"""
data {output_caslib}.{output_table};
    set {input_caslib}.{input_name};
    {self.column_name} = _threadid_ * 1000000000 + _N_;
run;
"""
        return code.strip()
