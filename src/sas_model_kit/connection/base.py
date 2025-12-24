"""
Connection protocol definition.

This module defines the ConnectionProtocol interface that all connection
implementations must follow (SRP - Single Responsibility Principle).

Connection responsibilities:
- Establish and manage session lifecycle
- Monitor connection health
- Auto-reconnect when needed
- Provide access to underlying session

NOT responsible for:
- Data upload/download (delegated to data_management layer)
- Action execution (delegated to Model layer)
"""

from types import TracebackType
from typing import Protocol, TypeVar

LibraryConnectionT = TypeVar("LibraryConnectionT", covariant=True)


class ConnectionProtocol(Protocol[LibraryConnectionT]):
    """
    Protocol for connection implementations.

    All connection classes (SWAT, SASCTL, HTTPx) must implement this interface
    following the Single Responsibility Principle.

    Methods:
        connect(): Establish connection to server
        is_healthy(): Check if connection is alive and healthy
        reconnect(): Close and re-establish connection
        close(): Close connection and release resources
        get_session(): Get underlying session object for operations

    Example:
        >>> # Any implementation following this protocol
        >>> connection: ConnectionProtocol = SWATConnection('host', 5570)
        >>> with connection:
        ...     session = connection.get_session()
        ...     # Use session for data/action operations
    """

    _session: LibraryConnectionT | None = None

    def connect(self) -> None:
        """
        Establish connection to server.

        Raises:
            ConnectionError: If connection fails
        """
        ...

    def is_healthy(self) -> bool:
        """
        Check if connection is alive and healthy.

        Returns:
            True if connection is healthy, False otherwise
        """
        ...

    def reconnect(self) -> None:
        """
        Reconnect to server.

        This closes existing connection (if any) and establishes a new one.

        Raises:
            ConnectionError: If reconnection fails
        """
        ...

    def close(self) -> None:
        """
        Close connection and release resources.

        Raises:
            ConnectionError: If closing fails
        """
        ...

    def get_session(self) -> LibraryConnectionT:
        """
        Get underlying session object.

        This session is used by data_management and model layers for
        performing operations like upload_data, call_action, etc.

        Returns:
            The underlying session object (e.g., swat.CAS)

        Raises:
            ConnectionError: If connection is not established or unhealthy
        """
        ...

    def __enter__(self) -> "ConnectionProtocol[LibraryConnectionT]":
        """
        Context manager entry.

        Ensures connection is established or reconnected if unhealthy.
        """
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """
        Context manager exit.

        Note: Connection remains open for reuse. Use close() for explicit cleanup.
        """
        ...
