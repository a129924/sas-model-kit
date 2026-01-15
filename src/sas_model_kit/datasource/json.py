"""
JSON data source implementation.

This module implements DataSourceProtocol for JSON-serializable data,
providing dictionary-based result retrieval.
"""

from typing import Any

import pandas as pd
from typing_extensions import override

from sas_model_kit.datasource.base import DataSourceProtocol
from sas_model_kit.error import DataFetchFailure, OperationError, UploadFailure
from sas_model_kit.operation.base import OperationProtocol
from sas_model_kit.result import Err, Ok, Result


class JSONDataSource(DataSourceProtocol[dict[str, Any] | list[dict[str, Any]]]):
    """
    Data source for JSON-serializable data.

    Implements DataSourceProtocol[dict] for scenarios requiring structured
    dictionary results instead of DataFrame. Following CSRP (Concrete Single
    Responsibility Principle).

    Useful for:
    - API responses
    - Metadata retrieval
    - Structured model outputs (e.g., explainModel results)

    Attributes:
        _data: Source data (DataFrame or dict) to upload
        _caslib: Target CAS library for upload
        _table: Target table name for upload

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'x': [1, 2, 3]})
        >>>
        >>> # Create data source
        >>> datasource = JSONDataSource(
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
        >>> # Fetch results as dict
        >>> result_dict = datasource.fetch_result(
        ...     operation,
        ...     caslib='public',
        ...     table='output_data'
        ... )
    """

    def __init__(
        self,
        data: pd.DataFrame | dict[str, Any] | list[dict[str, Any]],
        caslib: str,
        table: str,
    ) -> None:
        """
        Initialize JSON data source.

        Args:
            data: Source data to upload (DataFrame or dict)
            caslib: Target CAS library for upload
            table: Target table name for upload

        Raises:
            TypeError: If data is not DataFrame or dict
            ValueError: If caslib or table is empty

        Example:
            >>> df = pd.DataFrame({'a': [1, 2]})
            >>> datasource = JSONDataSource(df, 'public', 'my_data')
        """
        if not isinstance(data, (pd.DataFrame, dict)):
            raise TypeError(f"Expected DataFrame or dict, got {type(data).__name__}")

        if not caslib or not caslib.strip():
            raise ValueError("caslib cannot be empty")

        if not table or not table.strip():
            raise ValueError("table cannot be empty")

        self._data = data
        self._caslib = caslib
        self._table = table

    @override
    def prepare(self, operation: OperationProtocol) -> Result[None, UploadFailure]:
        """Upload data to CAS server and return Result."""

        def _to_upload_failure(error: OperationError) -> UploadFailure:
            return UploadFailure(
                code=str(error.code.value),
                message=error.message,
                cause=error.cause,
            )

        upload_data = (
            pd.DataFrame(self._data) if isinstance(self._data, dict) else self._data
        )

        return (
            operation.upload_data(upload_data, caslib=self._caslib, table=self._table)
            .map(lambda _: None)
            .map_err(_to_upload_failure)
        )

    @override
    def fetch_result(
        self, operation: OperationProtocol, caslib: str, table: str
    ) -> Result[dict[str, Any] | list[dict[str, Any]], DataFetchFailure]:
        """Fetch results from CAS as dictionary and return Result."""

        def _to_fetch_failure(error: OperationError) -> DataFetchFailure:
            return DataFetchFailure(
                code=str(error.code.value),
                message=error.message,
                cause=error.cause,
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

            return Ok(df.to_dict(orient="list"))

        return Err(
            DataFetchFailure(
                code="FETCH_RESULT_FORMAT_INVALID",
                message=f"Unexpected result format from table.fetch: {type(result)}",
                context={"caslib": caslib, "table": table},
            )
        )
