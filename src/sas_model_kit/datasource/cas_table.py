"""
CAS table data source implementation.

This module implements DataSourceProtocol for existing CAS tables, enabling
models to work with data already on the server without upload/download.
"""

import pandas as pd
from typing_extensions import override

from sas_model_kit.datasource.base import DataSourceProtocol
from sas_model_kit.operation.base import OperationProtocol


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

    @override
    def prepare(self, operation: OperationProtocol) -> None:
        """
        Validate that CAS table exists.

        Unlike DataFrameDataSource, this does NOT upload data since the
        table should already exist on the server. Only validates existence.

        Args:
            operation: Operation adapter for validation

        Raises:
            ValueError: If table does not exist
            RuntimeError: If validation fails

        Example:
            >>> datasource.prepare(operation)
            # Validates public.existing_data exists
        """
        try:
            # Use table.tableExists action to validate
            result = operation.call_action(
                "table.tableExists", caslib=self._caslib, name=self._table
            )

            # Check if table exists
            # SWAT returns results in result['exists'] format
            if hasattr(result, "__getitem__") and hasattr(result, "get"):
                exists = result.get("exists", False)

                if not exists:
                    raise ValueError(
                        f"Table {self._caslib}.{self._table} does not exist"
                    )
            else:
                raise ValueError(
                    f"Unexpected result format from table.tableExists: {type(result)}"
                )

        except ValueError:
            # Re-raise ValueError as-is
            raise

        except Exception as e:
            raise RuntimeError(
                f"Failed to validate CAS table {self._caslib}.{self._table}: {e}"
            ) from e

    @override
    def fetch_result(
        self, operation: OperationProtocol, caslib: str, table: str
    ) -> pd.DataFrame:
        """
        Fetch results from CAS as DataFrame.

        Downloads the specified CAS table and returns it as a pandas DataFrame.
        Uses SWAT's fetch() action for efficient data retrieval.

        Implementation is identical to DataFrameDataSource.fetch_result()
        since both return DataFrame from CAS tables.

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

    @property
    def caslib(self) -> str:
        """Get source CAS library name."""
        return self._caslib

    @property
    def table(self) -> str:
        """Get source table name."""
        return self._table
