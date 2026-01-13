"""
CAS table data source implementation.

This module implements DataSourceProtocol for existing CAS tables, enabling
models to work with data already on the server without upload/download.
"""

import pandas as pd
from swat.cas.results import CASResults
from typing_extensions import override

from sas_model_kit.datasource.base import DataSourceProtocol
from sas_model_kit.error import DataFetchFailure, OperationError, UploadFailure
from sas_model_kit.operation.base import OperationProtocol
from sas_model_kit.result import Err, Ok, Result


class CASTableDataSource(DataSourceProtocol[pd.DataFrame]):
    """
    Data source for existing CAS tables.

    Implements DataSourceProtocol[pd.DataFrame] for scenarios where data
    already exists on the CAS server. Following CSRP (Concrete Single
    Responsibility Principle).

    Unlike DataFrameDataSource, this does NOT upload data during prepare()
    since the table already exists. It only validates table existence.

    Attributes:
        _caslib: Source CAS library
        _table: Source table name

    Example:
        >>> # Use existing CAS table (no upload needed)
        >>> datasource = CASTableDataSource(
        ...     caslib='public',
        ...     table='existing_data'
        ... )
        >>>
        >>> # Prepare (validates existence only)
        >>> operation = connection.get_operation()
        >>> datasource.prepare(operation)
        >>>
        >>> # Execute model (not shown)
        >>> # ...
        >>>
        >>> # Fetch results
        >>> result_df = datasource.fetch_result(
        ...     operation,
        ...     caslib='public',
        ...     table='scored_data'
        ... )
    """

    def __init__(self, caslib: str, table: str) -> None:
        """
        Initialize CAS table data source.

        Args:
            caslib: Source CAS library
            table: Source table name

        Raises:
            ValueError: If caslib or table is empty

        Example:
            >>> datasource = CASTableDataSource('public', 'my_data')
        """
        if not caslib or not caslib.strip():
            raise ValueError("caslib cannot be empty")

        if not table or not table.strip():
            raise ValueError("table cannot be empty")

        self._caslib = caslib
        self._table = table

    def _process_success(self, result: CASResults):
        """Process successful CASResults (placeholder)."""
        pass

    @staticmethod
    def _to_upload_failure(error: OperationError) -> UploadFailure:
        """Convert OperationError to UploadFailure."""
        return UploadFailure(
            code=error.code,
            message=error.message,
            severity=error.severity,
            cause=error.cause,
            context=error.context,
        )

    def _validate_table_exists(self, exists: bool) -> Result[None, UploadFailure]:
        """Validate that table exists."""
        if not exists:
            return Err(
                UploadFailure(
                    code="TABLE_NOT_FOUND",
                    message=f"Table {self._caslib}.{self._table} does not exist",
                    context={"caslib": self._caslib, "table": self._table},
                )
            )
        return Ok(None)

    @override
    def prepare(self, operation: OperationProtocol) -> Result[None, UploadFailure]:
        """Validate that CAS table exists, returning Result.

        Uses and_then for clean error propagation and chaining.
        """
        return (
            operation.table_exists(self._caslib, self._table)
            .map_err(self._to_upload_failure)
            .and_then(self._validate_table_exists)
        )

    @override
    def fetch_result(
        self, operation: OperationProtocol, caslib: str, table: str
    ) -> Result[pd.DataFrame, DataFetchFailure]:
        """Fetch results from CAS as DataFrame and return Result."""

        def _to_fetch_failure(error: OperationError) -> DataFetchFailure:
            return DataFetchFailure(
                code=error.code,
                message=error.message,
                severity=error.severity,
                cause=error.cause,
                context=error.context,
            )

        action_result = operation.call_action(
            "table.fetch", table={"name": table, "caslib": caslib}
        )

        if action_result.is_err:
            return Err(_to_fetch_failure(action_result.error))

        result = action_result.value

        if hasattr(result, "__getitem__") and "Fetch" in result:
            df = result["Fetch"]

            if not isinstance(df, pd.DataFrame):
                return Err(
                    DataFetchFailure(
                        code="FETCH_RESULT_TYPE_INVALID",
                        message=(
                            f"Expected DataFrame from fetch, got {type(df).__name__}"
                        ),
                        context={"caslib": caslib, "table": table},
                    )
                )

            return Ok(df)

        return Err(
            DataFetchFailure(
                code="FETCH_RESULT_FORMAT_INVALID",
                message=f"Unexpected result format from table.fetch: {type(result)}",
                context={"caslib": caslib, "table": table},
            )
        )

    @property
    def caslib(self) -> str:
        """Get source CAS library name."""
        return self._caslib

    @property
    def table(self) -> str:
        """Get source table name."""
        return self._table
