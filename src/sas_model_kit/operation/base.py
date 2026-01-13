"""
Operation protocol definition.

This module defines the OperationProtocol interface that all operation
implementations must follow (SRP - Single Responsibility Principle).

Operation responsibilities:
- Execute SAS actions via underlying session
- Upload data to CAS/Server
- NOT responsible for: Connection lifecycle (delegated to SessionProtocol)
"""

from abc import ABC, abstractmethod
from typing import Any, Final, Generic, Protocol, TypeVar

from sas_model_kit.error import OperationError
from sas_model_kit.error.operation import TableNotFoundError
from sas_model_kit.result import Result

ReSourceType = TypeVar("ReSourceType", contravariant=True)
ReturnType = TypeVar("ReturnType", covariant=True)
LibraryConnectionT = TypeVar("LibraryConnectionT", covariant=True)


class OperationProtocol(
    Protocol[ReSourceType, ReturnType],
):
    """
    Protocol for operation implementations.

    All operation adapters (SWAT, SASCTL, HTTPx) must implement this interface
    following the Single Responsibility Principle.

    Operations are stateless and focus solely on executing actions and
    uploading data. Connection management is handled by SessionProtocol.

    Methods:
        call_action(): Execute a SAS action
        upload_data(): Upload data to server
        table_exists(): Check if table exists in CAS library
        model_exists(): Check if model (ASTORE) exists in CAS library

    Example:
        >>> # SWATOperationAdapter implements this protocol
        >>> operation: OperationProtocol = connection.get_operation()
        >>> result = operation.call_action('astore.score', table='input', ...)
        >>> operation.upload_data(df, caslib='public', table='data')
        >>> if operation.table_exists('public', 'my_table'):
        ...     print("Table exists")
    """

    def call_action(
        self, action_name: str, **kwargs: Any
    ) -> Result[Any, OperationError]:
        """
        Execute a SAS action.

        Args:
            action_name: Action to execute (format: 'actionset.action')
                        Examples: 'astore.score', 'explainModel.explain'
            **kwargs: Action-specific parameters

        Returns:
            Action execution result (format depends on implementation)

        Raises:
            ExecutionError: If action execution fails
            ValueError: If action_name format is invalid

        Example:
            >>> operation.call_action(
            ...     'astore.score',
            ...     table={'name': 'input_data'},
            ...     rstore={'name': 'my_model'},
            ...     out={'name': 'scored_data', 'replace': True}
            ... )
        """
        ...

    def upload_data(
        self, data: ReSourceType, caslib: str, table: str
    ) -> Result[ReturnType, OperationError]:
        """
        Upload data to server.

        Args:
            data: Data to upload (DataFrame, dict, list, etc.)
            caslib: Target CAS library
            table: Target table name

        Returns:
            ReturnType: Implementation-specific return value (e.g., CASTable for SWAT)

        Raises:
            ExecutionError: If upload fails
            ValueError: If data format is unsupported

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
            >>> cas_table = operation.upload_data(df, caslib='public', table='my_data')
        """
        ...

    def table_exists(
        self, caslib: str, table: str
    ) -> Result[bool, TableNotFoundError | OperationError]:
        """
        Check if a table exists in the specified CAS library.

        Args:
            caslib: CAS library name
            table: Table name to check

        Returns:
            True if table exists, False otherwise

        Example:
            >>> if operation.table_exists('public', 'my_data'):
            ...     print("Table exists")
        """
        ...

    def model_exists(self, caslib: str, table: str) -> Result[bool, OperationError]:
        """
        Check if a model (ASTORE) exists in the specified CAS library.

        Args:
            caslib: CAS library name containing models
            table: Model table name (ASTORE) to check

        Returns:
            True if model exists, False otherwise

        Example:
            >>> if operation.model_exists('models', 'my_astore'):
            ...     print("Model exists")
        """
        ...

    def drop_table(self, caslib: str, table: str) -> None:
        """
        Drop a table from the specified CAS library.

        Args:
            caslib: CAS library name
            table: Table name to drop
        Returns:
            None
        Example:
            >>> operation.drop_table('public', 'my_data')
        """
        ...


class BaseOperation(
    ABC,
    OperationProtocol[ReSourceType, ReturnType],
    Generic[LibraryConnectionT, ReSourceType, ReturnType],
):
    """
    Abstract base class for operation implementations (CSRP).

    This class provides a skeletal implementation of the OperationProtocol
    to minimize the effort required to implement this interface.

    Subclasses must implement the abstract methods defined here.

    Methods:
        call_action(): Execute a SAS action
        upload_data(): Upload data to server

    Example:
        >>> class MyOperation
        ...     (BaseOperation):
        ...     def call_action(self, action_name: str, **kwargs: Any) -> Any:
        ...         # Implement action execution logic
        ...         pass
        ...     def upload_data(self, data: Any, caslib: str, table: str) -> None:
        ...         # Implement data upload logic
        ...         pass
    """

    def __init__(self, connection: LibraryConnectionT) -> None:
        """
        Initialize operation with library connection.

        Args:
            connection: Library connection instance

        Example:
            >>> operation = MyOperation(connection)
        """
        self._check_connection_type(connection)

        self._session: Final[LibraryConnectionT] = connection

    @abstractmethod
    def _check_connection_type(self, connection: Any) -> None:
        """
        Validate connection type.

        Args:
            connection: Connection instance to validate

        Raises:
            TypeError: If connection type is invalid

        Example:
            >>> cls._check_connection_type(connection)
        """
        ...

    @abstractmethod
    def call_action(
        self, action_name: str, **kwargs: Any
    ) -> Result[Any, OperationError]: ...
    @abstractmethod
    def upload_data(
        self, data: ReSourceType, caslib: str, table: str
    ) -> Result[ReturnType, OperationError]: ...
    @abstractmethod
    def table_exists(self, caslib: str, table: str) -> Result[bool, OperationError]: ...
    @abstractmethod
    def model_exists(self, caslib: str, table: str) -> Result[bool, OperationError]: ...
    @abstractmethod
    def drop_table(self, caslib: str, table: str) -> None: ...
