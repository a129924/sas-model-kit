"""
DataFrame data source implementation.

This module implements DataSourceProtocol for pandas DataFrame, providing
upload/download capabilities for tabular data.
"""

from typing import Any, TypeVar

import pandas as pd
from typing_extensions import override

from sas_model_kit.datasource.base import DataSourceProtocol
from sas_model_kit.error import DataFetchFailure, OperationError, UploadFailure
from sas_model_kit.operation.base import OperationProtocol
from sas_model_kit.result import Err, Ok, Result

# Type variables for generic OperationProtocol support
OperationReturnType = TypeVar("OperationReturnType")  # Any type the operation returns


class DataFrameDataSource(DataSourceProtocol[pd.DataFrame]):
    """
    Data source for pandas DataFrame.

    Implements DataSourceProtocol[pd.DataFrame] following CSRP (Concrete
    Single Responsibility Principle). Handles upload of DataFrame to CAS
    and download of results back to DataFrame.

    Attributes:
        _data: Source DataFrame to upload
        _caslib: Target CAS library for upload
        _table: Target table name for upload

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        >>>
        >>> # Create data source
        >>> datasource = DataFrameDataSource(
        ...     data=df,
        ...     caslib='public',
        ...     table='input_data'
        ... )
        >>>
        >>> # Prepare for execution
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

    def __init__(self, data: pd.DataFrame, caslib: str, table: str) -> None:
        """
        Initialize DataFrame data source.

        Args:
            data: Source DataFrame to upload
            caslib: Target CAS library for upload
            table: Target table name for upload

        Raises:
            TypeError: If data is not a pandas DataFrame
            ValueError: If caslib or table is empty

        Example:
            >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
            >>> datasource = DataFrameDataSource(df, 'public', 'my_data')
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(data).__name__}")

        if not caslib or not caslib.strip():
            raise ValueError("caslib cannot be empty")

        if not table or not table.strip():
            raise ValueError("table cannot be empty")

        self._data = data
        self._caslib = caslib
        self._table = table

    @override
    def prepare(
        self, operation: OperationProtocol[pd.DataFrame, Any]
    ) -> Result[None, UploadFailure]:
        """Upload DataFrame to CAS server and return Result."""

        def _to_upload_failure(error: OperationError) -> UploadFailure:
            return UploadFailure(
                code=error.code,
                message=error.message,
                severity=error.severity,
                cause=error.cause,
                context=error.context,
            )

        return (
            operation.upload_data(self._data, caslib=self._caslib, table=self._table)
            .map(lambda _: None)
            .map_err(_to_upload_failure)
        )

    @override
    def fetch_result(
        self, operation: OperationProtocol[pd.DataFrame, Any], caslib: str, table: str
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

        match action_result:
            case Err():
                return Err(_to_fetch_failure(action_result.error))
            case Ok(result):
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
