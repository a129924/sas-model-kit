"""SWAT implementation of all 8 Able Protocols.

This module provides SWATOperationsImpl, a class that implements all 8 Able
protocols defined in helpers.protocols. It serves as a SWAT-specific adapter
for framework operations.

Design Pattern:
    - Single class implements all 8 protocols (convenience over separation)
    - Each method delegates to OperationProtocol or uses SWAT native APIs
    - Returns Result[T, OperationError] for consistent error handling
    - Zero conversion cost for ValidateAble (uses native exists())

Usage Example:
    >>> from sas_model_kit.helpers.swat.operations import SWATOperationsImpl
    >>> ops = SWATOperationsImpl(operation)
    >>>
    >>> # Use as ReadAble
    >>> columns_result = ops.get_columns(table)
    >>>
    >>> # Use as ValidateAble
    >>> validated = ops.ensure_exists(cas_table)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sas_model_kit.error import OperationError, OperationErrorCode, TableNotFoundError
from sas_model_kit.helpers.swat.types import SwatTableT
from sas_model_kit.result import Err, Ok, Result

if TYPE_CHECKING:
    from sas_model_kit.operation import OperationProtocol


class SWATOperationsImpl:
    """SWAT adapter implementing all 8 Able Protocols.

    This class provides concrete implementations of:
    - ReadAble: get_columns, get_table_location
    - WriteAble: create_table
    - SortAble: sort_values
    - DeleteAble: drop_table
    - ConcatAble: concat_tables
    - ValidateAble: ensure_exists
    - ActionExecutable: execute_action
    - ResultParseable: extract_astore_payload, extract_shapley_values, extract_status

    Attributes:
        operation: OperationProtocol instance for action execution
    """

    def __init__(self, operation: OperationProtocol) -> None:
        """Initialize SWAT operations adapter.

        Args:
            operation: OperationProtocol instance for executing CAS actions
        """
        self.operation = operation

    # ========== ReadAble Implementation ==========

    def get_columns(self, table: Any) -> Result[list[str], OperationError]:
        """Get all column names from the table.

        Args:
            table: CASTable object

        Returns:
            Ok(list[str]): List of column names
            Err(OperationError): Failed to read columns
        """
        try:
            return Ok(list(table.columns))
        except Exception as e:
            return Err(
                OperationError(
                    code=OperationErrorCode.READ_FAILED,
                    message=f"Failed to get columns: {e}",
                    cause=e,
                )
            )

    def get_table_location(self, table: Any) -> Result[tuple[str, str], OperationError]:
        """Get table location as (caslib, table_name).

        Args:
            table: CASTable object

        Returns:
            Ok(tuple[str, str]): (caslib, table_name)
            Err(OperationError): Failed to get location
        """
        try:
            caslib = table.params.get("caslib", "public")
            name = table.params["name"]
            return Ok((caslib, name))
        except Exception as e:
            return Err(
                OperationError(
                    code=OperationErrorCode.READ_FAILED,
                    message=f"Failed to get table location: {e}",
                    cause=e,
                )
            )

    # ========== WriteAble Implementation ==========

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
            source: Data source (DataFrame, CASTable, etc.)
            replace: Whether to replace existing table

        Returns:
            Ok(CASTable): Reference to created table
            Err(OperationError): Failed to create table
        """
        try:
            # Upload data to CAS and create table reference
            upload_result = self.operation.upload_data(
                data=source,
                caslib=caslib,
                table=name,
                replace=replace,
            )

            if upload_result.is_err:
                return Err(
                    OperationError(
                        code=OperationErrorCode.WRITE_FAILED,
                        message=f"Failed to upload data for table '{name}': {upload_result.error}",
                        cause=upload_result.error,
                    )
                )

            # Create CASTable reference
            connection = self.operation._session
            new_table = connection.CASTable(name=name, caslib=caslib)
            return Ok(new_table)

        except Exception as e:
            return Err(
                OperationError(
                    code=OperationErrorCode.WRITE_FAILED,
                    message=f"Failed to create table '{name}': {e}",
                    cause=e,
                )
            )

    # ========== SortAble Implementation ==========

    def sort_values(
        self,
        table: Any,
        by: list[str],
        ascending: bool | list[bool] = True,
    ) -> Result[Any, OperationError]:
        """Sort table by specified columns.

        Args:
            table: CASTable to sort
            by: Column names to sort by
            ascending: Sort order

        Returns:
            Ok(CASTable): Reference to sorted table
            Err(OperationError): Failed to sort table
        """
        try:
            sorted_table = table.sort_values(by=by, ascending=ascending)
            return Ok(sorted_table)
        except Exception as e:
            return Err(
                OperationError(
                    code=OperationErrorCode.SORT_FAILED,
                    message=f"Failed to sort table by {by}: {e}",
                    cause=e,
                )
            )

    # ========== DeleteAble Implementation ==========

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
        return self.operation.call_action(
            "table.dropTable",
            caslib=caslib,
            name=table,
        ).map(lambda _: None)

    # ========== ConcatAble Implementation ==========

    def concat_tables(
        self,
        inputs: list[Any],
        caslib: str,
        output_table: str,
        replace: bool = True,
    ) -> Result[Any, OperationError]:
        """Concatenate multiple tables into one.

        Args:
            inputs: List of tables to concatenate
            caslib: Output CAS library name
            output_table: Output table name
            replace: Whether to replace existing output table

        Returns:
            Ok(CASTable): Reference to concatenated table
            Err(OperationError): Failed to concatenate tables
        """
        concat_result = self.operation.call_action(
            "table.concat",
            casout={"name": output_table, "caslib": caslib, "replace": replace},
            inputs=inputs,
        )

        if concat_result.is_err:
            return Err(concat_result.error)

        # Create CASTable reference to result
        connection = self.operation._session
        result_table = connection.CASTable(name=output_table, caslib=caslib)
        return Ok(result_table)

    # ========== ValidateAble Implementation ==========

    def ensure_exists(
        self, library_table: SwatTableT
    ) -> Result[SwatTableT, TableNotFoundError]:
        """Validate CAS table exists using native exists() method.

        Uses swat.CASTable.exists() native API directly to check table existence.
        Zero-conversion cost: Returns the same library_table object if exists.

        Args:
            library_table: CASTable object to validate

        Returns:
            Ok(SwatTableT): Table exists, returns same library_table object
            Err(TableNotFoundError): Table not found or validation failed
        """
        try:
            if library_table.exists():
                # Return same object (zero conversion cost)
                return Ok(library_table)
            else:
                table_name = library_table.params.get("name", "unknown")
                caslib = library_table.params.get("caslib", "ACTIVE")
                return Err(
                    TableNotFoundError(
                        message=f"Table '{table_name}' not found in caslib '{caslib}'"
                    )
                )
        except Exception as e:
            return Err(
                TableNotFoundError(
                    message=f"Failed to check table existence: {e}",
                    cause=e,
                )
            )

    # ========== ActionExecutable Implementation ==========

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
        return self.operation.call_action(action, **kwargs)

    # ========== ResultParseable Implementation ==========

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
        try:
            # SWAT-specific: astore.score returns payload in specific structure
            if hasattr(result, "get"):
                # Try to get OutputCasTables first
                output_tables = result.get("OutputCasTables", None)
                if output_tables is not None:
                    payload = {
                        "output_tables": output_tables.to_dict(orient="records"),
                    }
                    return Ok(payload)

            # If no payload found, return empty dict
            return Ok({})

        except Exception as e:
            return Err(
                OperationError(
                    code=OperationErrorCode.PARSE_FAILED,
                    message=f"Failed to extract astore payload: {e}",
                    cause=e,
                )
            )

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
        try:
            if hasattr(result, "get"):
                shapley = result.get("ShapleyValues", None)
                if shapley is not None:
                    return Ok(shapley.to_dict(orient="records"))

            # If no Shapley values found, return empty list
            return Ok([])

        except Exception as e:
            return Err(
                OperationError(
                    code=OperationErrorCode.PARSE_FAILED,
                    message=f"Failed to extract Shapley values: {e}",
                    cause=e,
                )
            )

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
        try:
            if hasattr(result, "get"):
                status = result.get("status")
                message = result.get("message") or "OK"

                # If status is explicitly a boolean, use it
                if isinstance(status, bool):
                    return Ok((status, str(message)))

            # Default to success if no status found
            return Ok((True, "OK"))

        except Exception as e:
            return Err(
                OperationError(
                    code=OperationErrorCode.PARSE_FAILED,
                    message=f"Failed to extract status: {e}",
                    cause=e,
                )
            )


__all__ = ["SWATOperationsImpl"]
