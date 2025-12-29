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

ReSourceType = TypeVar("ReSourceType", contravariant=True)
LibraryConnectionT = TypeVar("LibraryConnectionT", covariant=True)


class OperationProtocol(
    Protocol[ReSourceType],
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

    Example:
        >>> # SWATOperationAdapter implements this protocol
        >>> operation: OperationProtocol = connection.get_operation()
        >>> result = operation.call_action('astore.score', table='input', ...)
        >>> operation.upload_data(df, caslib='public', table='data')
    """

    def call_action(self, action_name: str, **kwargs: Any) -> Any:
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

    def upload_data(self, data: ReSourceType, caslib: str, table: str) -> None:
        """
        Upload data to server.

        Args:
            data: Data to upload (DataFrame, dict, list, etc.)
            caslib: Target CAS library
            table: Target table name

        Raises:
            ExecutionError: If upload fails
            ValueError: If data format is unsupported

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
            >>> operation.upload_data(df, caslib='public', table='my_data')
        """
        ...


class BaseOperation(
    ABC, OperationProtocol[ReSourceType], Generic[LibraryConnectionT, ReSourceType]
):
    """
    Abstract base class for operation implementations.

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
    def call_action(self, action_name: str, **kwargs: Any) -> Any: ...
    @abstractmethod
    def upload_data(self, data: ReSourceType, caslib: str, table: str) -> None: ...
