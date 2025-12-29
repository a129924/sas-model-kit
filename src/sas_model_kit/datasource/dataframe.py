"""
DataFrame data source implementation.

This module implements DataSourceProtocol for pandas DataFrame, providing
upload/download capabilities for tabular data.
"""

import pandas as pd
from typing_extensions import override

from sas_model_kit.datasource.base import DataSourceProtocol
from sas_model_kit.operation.base import OperationProtocol


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
    def prepare(self, operation: OperationProtocol[pd.DataFrame]) -> None:
        """
        Upload DataFrame to CAS server.

        Args:
            operation: Operation adapter for uploading data

        Raises:
            RuntimeError: If upload fails

        Example:
            >>> datasource.prepare(operation)
            # DataFrame uploaded to public.input_data
        """
        try:
            operation.upload_data(self._data, caslib=self._caslib, table=self._table)
        except Exception as e:
            raise RuntimeError(f"Failed to prepare DataFrame data source: {e}") from e

    @override
    def fetch_result(
        self, operation: OperationProtocol[pd.DataFrame], caslib: str, table: str
    ) -> pd.DataFrame:
        """
        Fetch results from CAS as DataFrame.

        Downloads the specified CAS table and returns it as a pandas DataFrame.
        Uses SWAT's fetch() action for efficient data retrieval.

        Args:
            operation: Operation adapter for fetching data
            caslib: Source CAS library containing results
            table: Source table name containing results

        Returns:
            Results as pandas DataFrame

        Raises:
            ValueError: If result cannot be converted to DataFrame
            RuntimeError: If fetch fails

        Example:
            >>> result_df = datasource.fetch_result(
            ...     operation,
            ...     caslib='public',
            ...     table='scored_data'
            ... )
        """
        try:
            # Use table.fetch action to retrieve data
            result = operation.call_action(
                "table.fetch", table={"name": table, "caslib": caslib}
            )

            # Extract DataFrame from CASResults
            # SWAT returns results in result['Fetch'] format
            if hasattr(result, "__getitem__") and "Fetch" in result:
                df = result["Fetch"]

                if not isinstance(df, pd.DataFrame):
                    raise ValueError(
                        f"Expected DataFrame from fetch, got {type(df).__name__}"
                    )

                return df

            else:
                raise ValueError(
                    f"Unexpected result format from table.fetch: {type(result)}"
                )

        except (ValueError, TypeError):
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch result from {caslib}.{table}: {e}"
            ) from e
