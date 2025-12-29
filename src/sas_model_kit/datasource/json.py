"""
JSON data source implementation.

This module implements DataSourceProtocol for JSON-serializable data,
providing dictionary-based result retrieval.
"""

import json
from typing import Any

import pandas as pd
from typing_extensions import override

from sas_model_kit.datasource.base import DataSourceProtocol
from sas_model_kit.operation.base import OperationProtocol


class JSONDataSource:
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
        data: pd.DataFrame | dict,
        caslib: str,
        table: str
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
            raise TypeError(
                f"Expected DataFrame or dict, got {type(data).__name__}"
            )

        if not caslib or not caslib.strip():
            raise ValueError("caslib cannot be empty")

        if not table or not table.strip():
            raise ValueError("table cannot be empty")

        self._data = data
        self._caslib = caslib
        self._table = table

    @override
    def prepare(self, operation: OperationProtocol) -> None:
        """
        Upload data to CAS server.

        Converts dict to DataFrame if needed before upload.

        Args:
            operation: Operation adapter for uploading data

        Raises:
            RuntimeError: If upload fails

        Example:
            >>> datasource.prepare(operation)
            # Data uploaded to public.input_data
        """
        try:
            # Convert dict to DataFrame if needed
            if isinstance(self._data, dict):
                # Assume dict is in records format: {'col1': [v1, v2], ...}
                upload_data = pd.DataFrame(self._data)
            else:
                upload_data = self._data

            operation.upload_data(
                upload_data,
                caslib=self._caslib,
                table=self._table
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to prepare JSON data source: {e}"
            ) from e

    @override
    def fetch_result(
        self,
        operation: OperationProtocol,
        caslib: str,
        table: str
    ) -> dict:
        """
        Fetch results from CAS as dictionary.

        Downloads the specified CAS table and converts it to a dictionary
        in records format: {'col1': [v1, v2, ...], 'col2': [v1, v2, ...]}

        Args:
            operation: Operation adapter for fetching data
            caslib: Source CAS library containing results
            table: Source table name containing results

        Returns:
            Results as dictionary

        Raises:
            ValueError: If result cannot be converted to dict
            RuntimeError: If fetch fails

        Example:
            >>> result_dict = datasource.fetch_result(
            ...     operation,
            ...     caslib='public',
            ...     table='output_data'
            ... )
            >>> # result_dict = {'col1': [1, 2], 'col2': [3, 4]}
        """
        try:
            # Use table.fetch action to retrieve data
            result = operation.call_action(
                'table.fetch',
                table={'name': table, 'caslib': caslib}
            )

            # Extract DataFrame from CASResults
            # SWAT returns results in result['Fetch'] format
            if hasattr(result, '__getitem__') and 'Fetch' in result:
                df = result['Fetch']

                if not isinstance(df, pd.DataFrame):
                    raise ValueError(
                        f"Expected DataFrame from fetch, got {type(df).__name__}"
                    )

                # Convert DataFrame to dict (records format)
                # to_dict(orient='list') gives {'col': [values]}
                return df.to_dict(orient='list')

            else:
                raise ValueError(
                    f"Unexpected result format from table.fetch: {type(result)}"
                )

        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch result from {caslib}.{table}: {e}"
            ) from e
