"""
SWAT connection implementation.

This module provides the SWATConnection class that manages CAS session
lifecycle following SRP (Single Responsibility Principle).

Connection responsibilities:
- Create and manage CAS session
- Check session health
- Auto-reconnect if disconnected
- Provide session access for operations

NOT responsible for:
- Data upload/download (delegated to data_management layer)
- Action execution (delegated to Model layer)
"""

try:
    import swat
except ImportError:
    raise ImportError(
        "SWAT is required for SWATConnection. Install it with: pip install swat"
    ) from ImportError

from sas_model_kit.connection.base import ConnectionProtocol


class SWATConnection(ConnectionProtocol[swat.CAS]):
    """
    SWAT implementation of ConnectionProtocol.

    This class manages the lifecycle of a swat.CAS session, following SRP
    by focusing only on connection management.

    Attributes:
        hostname: CAS server hostname
        port: CAS server port
        username: Username for authentication (optional)
        password: Password for authentication (optional)
        session: The underlying swat.CAS session (created after connect())

    Example:
        >>> # Manual connection management
        >>> connection = SWATConnection('hostname', 5570)
        >>> connection.connect()
        >>> if connection.is_healthy():
        ...     session = connection.get_session()
        ...     # Use session for operations
        >>> connection.close()

        >>> # Context manager (recommended)
        >>> with SWATConnection('hostname', 5570) as connection:
        ...     session = connection.get_session()
        ...     # Auto-checks health and reconnects if needed
    """

    def __init__(
        self,
        hostname: str,
        port: int = 5570,
        username: str | None = None,
        password: str | None = None,
        **kwargs,
    ):
        """
        Initialize SWATConnection with connection parameters.

        Args:
            hostname: CAS server hostname
            port: CAS server port (default: 5570)
            username: Username for authentication
            password: Password for authentication
            **kwargs: Additional parameters to pass to swat.CAS()

        Note:
            Connection is not established until connect() is called
            or when entering context manager.
        """
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self._kwargs = kwargs
        self._session: swat.CAS | None = None

    def connect(self) -> None:
        """
        Establish connection to CAS server.

        Raises:
            ConnectionError: If connection fails

        Example:
            >>> connection = SWATConnection('server', 5570)
            >>> connection.connect()
        """
        try:
            self._session = swat.CAS(
                self.hostname,
                self.port,
                username=self.username,
                password=self.password,
                **self._kwargs,
            )

            # Verify connection by checking server status
            if not self.is_healthy():
                raise ConnectionError(
                    f"Failed to establish healthy connection to "
                    f"{self.hostname}:{self.port}"
                )
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to CAS server {self.hostname}:{self.port}: {e}"
            ) from e

    def is_healthy(self) -> bool:
        """
        Check if the CAS session is alive and healthy.

        Returns:
            True if session is healthy, False otherwise

        Example:
            >>> if not connection.is_healthy():
            ...     connection.reconnect()
        """
        if self._session is None:
            return False

        try:
            # Check server status to verify connection
            result = self._session.serverstatus()
            return result is not None
        except Exception:
            return False

    def reconnect(self) -> None:
        """
        Reconnect to CAS server.

        This method:
        1. Closes existing session (if any)
        2. Re-establishes connection
        3. Verifies connection health

        Raises:
            ConnectionError: If reconnection fails

        Example:
            >>> connection.reconnect()
        """
        # Close existing session
        try:
            if self._session is not None:
                self._session.close()
        except Exception:
            # Ignore errors when closing dead connection
            pass
        finally:
            self._session = None

        # Re-establish connection
        self.connect()

    def close(self) -> None:
        """
        Close the CAS session.

        Raises:
            ConnectionError: If closing the session fails

        Example:
            >>> connection.close()
        """
        if self._session is None:
            return

        try:
            self._session.close()
        except Exception as e:
            raise ConnectionError(f"Failed to close CAS session: {e}") from e
        finally:
            self._session = None

    def get_session(self) -> swat.CAS:
        """
        Get the underlying CAS session for operations.

        This provides access to the swat.CAS session for data management
        and model layers to perform operations.

        Returns:
            The swat.CAS session object

        Raises:
            ConnectionError: If connection is not established

        Example:
            >>> session = connection.get_session()
            >>> session.upload_frame(df, casout='my_table')
        """
        if self._session is None:
            raise ConnectionError("Connection not established. Call connect() first.")

        if not self.is_healthy():
            raise ConnectionError("Connection is not healthy. Call reconnect().")

        return self._session

    def __enter__(self) -> "SWATConnection":
        """
        Context manager entry.

        Auto-connects if not already connected, or reconnects if unhealthy.

        Returns:
            self

        Example:
            >>> with SWATConnection('server', 5570) as conn:
            ...     session = conn.get_session()
        """
        if self._session is None:
            self.connect()
        elif not self.is_healthy():
            self.reconnect()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        Context manager exit.

        Note: Does NOT close the connection by default. Connection remains
        open for reuse. Next time __enter__ is called, it will check health
        and reconnect if needed.

        Returns:
            False to propagate exceptions
        """
        # Do not close connection - leave it open for next use
        # Next __enter__ will check health and reconnect if needed
        return False
