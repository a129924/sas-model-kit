"""
DataSource protocol definition.

This module defines the DataSourceProtocol interface that all data source
implementations must follow, inspired by PyTorch's Dataset pattern.

DataSource responsibilities (SRP - Single Responsibility Principle):
- Prepare data for upload to SAS server
- Fetch results from server after execution
- Handle data format conversion
- NOT responsible for: Connection management or action execution
"""

from typing import Generic, Protocol, TypeVar

from sas_model_kit.operation.base import OperationProtocol

# Generic type for data source return type
ReSourceT = TypeVar("ReSourceT", covariant=True)


class DataSourceProtocol(Protocol, Generic[ReSourceT]):
    """
    Protocol for data source implementations.

    Following PyTorch's Dataset pattern, DataSource provides a clean interface
    for preparing input data and fetching output results.

    Type parameter T represents the return type from fetch_result():
    - DataFrameDataSource[pd.DataFrame]
    - CASTableDataSource[pd.DataFrame]
    - JSONDataSource[dict]

    Methods:
        prepare(): Upload data to server before model execution
        fetch_result(): Retrieve results from server after execution

    Example:
        >>> # Prepare data
        >>> datasource = DataFrameDataSource(df, caslib='public', table='input')
        >>> datasource.prepare(operation)
        >>>
        >>> # Execute model (not DataSource's responsibility)
        >>> operation.call_action('astore.score', ...)
        >>>
        >>> # Fetch results
        >>> result_df = datasource.fetch_result(
        ...     operation,
        ...     caslib='public',
        ...     table='output'
        ... )
    """

    def prepare(self, operation: OperationProtocol) -> None:
        """
        Prepare data for server-side execution.

        This method uploads data to the SAS server using the provided
        operation adapter. Called before model execution.

        Args:
            operation: Operation adapter for uploading data

        Raises:
            ValueError: If data preparation fails
            RuntimeError: If upload fails

        Example:
            >>> datasource = DataFrameDataSource(df, 'public', 'input_data')
            >>> datasource.prepare(operation)
            # Now 'public.input_data' is available on server
        """
        ...

    def fetch_result(
        self, operation: OperationProtocol, caslib: str, table: str
    ) -> ReSourceT:
        """
        Fetch execution results from server.

        This method retrieves results from the SAS server after model
        execution. The return type T depends on the DataSource implementation:
        - DataFrameDataSource returns pd.DataFrame
        - JSONDataSource returns dict

        Args:
            operation: Operation adapter for fetching data
            caslib: Source CAS library containing results
            table: Source table name containing results

        Returns:
            Execution results in format T

        Raises:
            ValueError: If result format is invalid
            RuntimeError: If fetch fails

        Example:
            >>> # After model execution writes to 'public.scored_data'
            >>> result_df = datasource.fetch_result(
            ...     operation,
            ...     caslib='public',
            ...     table='scored_data'
            ... )
        """
        ...
