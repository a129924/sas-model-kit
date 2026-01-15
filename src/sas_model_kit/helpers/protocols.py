"""Capability-based Protocol definitions for SAS Model Kit.

This module defines 8 independent Able Protocols following the Capability-Based
Architecture pattern. Each protocol represents a single capability (verb) with
1-5 related methods, adhering to CSRP (Cohesion Single Responsibility Principle).

Protocol List:
    1. ReadAble: Read table metadata (columns, location)
    2. WriteAble: Create/write tables
    3. SortAble: Sort table data
    4. DeleteAble: Delete tables
    5. ConcatAble: Concatenate multiple tables
    6. ValidateAble: Validate table existence (using SWAT native API)
    7. ActionExecutable: Execute SWAT actions
    8. ResultParseable: Parse SWAT action results

Design Principles:
    - Single Responsibility: Each protocol has one capability
    - Interface Segregation: Depend only on what you need
    - Dependency Inversion: Depend on abstractions, not implementations
    - Type Safety: Generic type T (framework-agnostic)

Usage Example:
    >>> # Transformer depends only on SortAble
    >>> class SortTransformer:
    ...     def __init__(self, sortable: SortAble):
    ...         self.sortable = sortable
    ...
    ...     def execute(self, table):
    ...         return self.sortable.sort_values(table, by=["col1"])
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, TypeVar

from sas_model_kit.error import DataError, OperationError, TableNotFoundError
from sas_model_kit.result import Result

if TYPE_CHECKING:
    from sas_model_kit.operation import OperationProtocol

T = TypeVar("T")


class ReadAble(Protocol[T]):
    """Capability to read table metadata.

    Provides methods to retrieve table information such as column names
    and table location (caslib, table_name).

    Methods:
        get_columns: Retrieve all column names from a table
        get_table_location: Get table location as (caslib, table_name) tuple
    """

    def get_columns(self, table: T) -> Result[list[str], OperationError]:
        """Get all column names from the table.

        Args:
            table: Table object to inspect (e.g., swat.CASTable)

        Returns:
            Ok(list[str]): List of column names
            Err(OperationError): Failed to read columns
        """
        ...

    def get_table_location(self, table: T) -> Result[tuple[str, str], OperationError]:
        """Get table location as (caslib, table_name).

        Args:
            table: Table object to inspect

        Returns:
            Ok(tuple[str, str]): (caslib, table_name)
            Err(OperationError): Failed to get location
        """
        ...


class WriteAble(Protocol):
    """Capability to create and write tables.

    Provides methods to create new tables or replace existing ones.

    Methods:
        create_table: Create or replace a table
    """

    def create_table(
        self,
        name: str,
        caslib: str,
        source: Any,
        replace: bool = False,
    ) -> Result[Any, OperationError]:
        """Create or replace a table.

        Args:
            name: Table name
            caslib: CAS library name
            source: Data source (e.g., DataFrame, CASTable)
            replace: Whether to replace existing table

        Returns:
            Ok(CASTable): Reference to created table
            Err(OperationError): Failed to create table
        """
        ...


class SortAble(Protocol[T]):
    """Capability to sort table data.

    Provides methods to sort tables by one or more columns.

    Methods:
        sort_values: Sort table by specified columns
    """

    def sort_values(
        self,
        table: T,
        by: list[str],
        ascending: bool | list[bool] = True,
    ) -> Result[T, DataError | OperationError]:
        """Sort table by specified columns.

        Args:
            table: Table to sort
            by: Column names to sort by
            ascending: Sort order (True=ascending, False=descending)

        Returns:
            Ok(CASTable): Reference to sorted table
            Err(DataError | OperationError): Failed to sort table
        """
        ...


class DeleteAble(Protocol):
    """Capability to delete tables.

    Provides methods to remove tables from CAS.

    Methods:
        drop_table: Delete a table
    """

    def drop_table(
        self,
        caslib: str,
        table: str,
    ) -> Result[None, OperationError]:
        """Delete a table from CAS.

        Args:
            caslib: CAS library name
            table: Table name to delete

        Returns:
            Ok(None): Table deleted successfully
            Err(OperationError): Failed to delete table
        """
        ...


class ConcatAble(Protocol[T]):
    """Capability to concatenate multiple tables.

    Provides methods to merge multiple tables into one.

    Methods:
        concat_tables: Concatenate multiple tables
    """

    def concat_tables(
        self,
        inputs: list[T],
        caslib: str,
        output_table: str,
        replace: bool = True,
    ) -> Result[T, DataError | OperationError]:
        """Concatenate multiple tables into one.

        Args:
            inputs: List of tables to concatenate
            caslib: Output CAS library name
            output_table: Output table name
            replace: Whether to replace existing output table

        Returns:
            Ok(CASTable): Reference to concatenated table
            Err(DataError | OperationError): Failed to concatenate tables
        """
        ...


class ValidateAble(Protocol[T]):
    """Capability to validate table existence.

    Uses SWAT native library_table.exists() API directly, avoiding
    manual call_action operations. Zero-conversion cost: receives
    library_table and returns the same object after validation.

    Type Parameter:
        T: Table type that provides a native ``exists()`` method

    Design Advantages:
        - Zero conversion cost: No unpacking/repacking of parameters
        - Native API usage: Direct library_table.exists() call
        - Type safe: TypeVar T ensures correct types
        - Simple: Single parameter (library_table) instead of 3

    Methods:
        ensure_exists: Validate table exists, return same object
    """

    operation: OperationProtocol  # Reserved for future use

    def ensure_exists(
        self,
        library_table: T,
    ) -> Result[T, TableNotFoundError]:
        """Validate CAS table exists, return same object.

        Uses swat.CASTable.exists() native method to check existence.
        Returns the same library_table object if exists (no conversion).

        Args:
            library_table: CASTable object to validate (T bound to swat.CASTable)

        Returns:
            Ok(T): Table exists, returns same library_table object
            Err(TableNotFoundError): Table not found or validation failed

        Example:
            >>> result = validatable.ensure_exists(cas_table)
            >>> match result:
            ...     case Ok(table):
            ...         # table is the same object as cas_table
            ...         process(table)
            ...     case Err(TableNotFoundError()):
            ...         # Handle missing table
            ...         create_table()
        """
        ...


class ActionExecutable(Protocol):
    """Capability to execute SWAT actions.

    Provides methods to execute arbitrary SWAT actions with parameters.

    Methods:
        execute_action: Execute a SWAT action
    """

    def execute_action(
        self,
        action: str,
        **kwargs: Any,
    ) -> Result[Any, OperationError]:
        """Execute a SWAT action.

        Args:
            action: Action name (e.g., "astore.score")
            **kwargs: Action parameters

        Returns:
            Ok(Any): Action result (raw CASResults)
            Err(OperationError): Action execution failed
        """
        ...


class ModelResultParseable(Protocol):
    """Capability to parse SWAT action results.

    Provides methods to extract structured data from SWAT CASResults.

    Methods:
        extract_astore_payload: Extract astore.score results
        extract_shapley_values: Extract Shapley explanation values
        extract_status: Parse action status
    """

    def extract_astore_payload(
        self,
        result: Any,
    ) -> Result[dict[str, Any], OperationError]:
        """Extract astore.score payload from result.

        Args:
            result: CASResults from astore.score action

        Returns:
            Ok(dict): Extracted payload data
            Err(OperationError): Failed to parse payload
        """
        ...

    def extract_shapley_values(
        self,
        result: Any,
    ) -> Result[list[dict[str, Any]], OperationError]:
        """Extract Shapley values from result.

        Args:
            result: CASResults from explainModel.shapleyExplainer

        Returns:
            Ok(list[dict]): Shapley values as list of records
            Err(OperationError): Failed to parse Shapley values
        """
        ...

    def extract_status(
        self,
        result: Any,
    ) -> Result[tuple[bool, str], OperationError]:
        """Parse action status from result.

        Args:
            result: CASResults or any result object with status

        Returns:
            Ok(tuple[bool, str]): (success, status_message)
            Err(OperationError): Failed to parse status
        """
        ...


__all__ = [
    "ReadAble",
    "WriteAble",
    "SortAble",
    "DeleteAble",
    "ConcatAble",
    "ValidateAble",
    "ActionExecutable",
    "ModelResultParseable",
]
