"""
Unit tests for SWATConnection.

Tests verify that SWATConnection correctly implements ConnectionProtocol
following SRP (Single Responsibility Principle).

Connection responsibilities:
- Create and manage CAS session lifecycle
- Check session health
- Auto-reconnect when needed
- Provide session access

NOT tested here:
- Data upload/download (belongs to data_management layer)
- Action execution (belongs to Model layer)
"""

from unittest.mock import Mock, patch

import pytest

from sas_model_kit.connection.swat.connection import SWATConnection


class TestSWATConnectionInit:
    """Test SWATConnection initialization."""

    def test_init_with_required_params(self):
        """Test initialization with required parameters."""
        connection = SWATConnection("hostname", 5570)

        assert connection.hostname == "hostname"
        assert connection.port == 5570
        assert connection.username is None
        assert connection.password is None
        assert connection._session is None  # Not connected yet

    def test_init_with_all_params(self):
        """Test initialization with all parameters."""
        connection = SWATConnection(
            "hostname", 8888, username="user", password="pass", protocol="http"
        )

        assert connection.hostname == "hostname"
        assert connection.port == 8888
        assert connection.username == "user"
        assert connection.password == "pass"
        assert connection._kwargs == {"protocol": "http"}
        assert connection._session is None


class TestSWATConnectionConnect:
    """Test connection establishment."""

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_connect_success(self, mock_cas_class):
        """Test successful connection."""
        # Setup mock
        mock_session = Mock()
        mock_session.serverstatus.return_value = {"status": "ok"}
        mock_cas_class.return_value = mock_session

        # Test
        connection = SWATConnection("hostname", 5570, username="user", password="pass")
        connection.connect()

        # Verify
        mock_cas_class.assert_called_once_with(
            "hostname", 5570, username="user", password="pass"
        )
        assert connection._session == mock_session
        assert connection.is_healthy()

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_connect_with_kwargs(self, mock_cas_class):
        """Test connection with additional kwargs."""
        # Setup mock
        mock_session = Mock()
        mock_session.serverstatus.return_value = {"status": "ok"}
        mock_cas_class.return_value = mock_session

        # Test
        connection = SWATConnection("hostname", 5570, protocol="http", caslib="public")
        connection.connect()

        # Verify kwargs passed through
        mock_cas_class.assert_called_once_with(
            "hostname",
            5570,
            username=None,
            password=None,
            protocol="http",
            caslib="public",
        )

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_connect_failure(self, mock_cas_class):
        """Test connection failure."""
        # Setup mock to raise exception
        mock_cas_class.side_effect = Exception("Connection refused")

        # Test
        connection = SWATConnection("hostname", 5570)

        with pytest.raises(ConnectionError, match="Failed to connect"):
            connection.connect()

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_connect_unhealthy_session(self, mock_cas_class):
        """Test connection with unhealthy session."""
        # Setup mock that connects but serverstatus fails
        mock_session = Mock()
        mock_session.serverstatus.side_effect = Exception("Server error")
        mock_cas_class.return_value = mock_session

        # Test
        connection = SWATConnection("hostname", 5570)

        with pytest.raises(
            ConnectionError, match="Failed to establish healthy connection"
        ):
            connection.connect()


class TestSWATConnectionHealth:
    """Test connection health checks."""

    def test_is_healthy_when_not_connected(self):
        """Test health check when not connected."""
        connection = SWATConnection("hostname", 5570)
        assert not connection.is_healthy()

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_is_healthy_when_connected(self, mock_cas_class):
        """Test health check when connected."""
        # Setup mock
        mock_session = Mock()
        mock_session.serverstatus.return_value = {"status": "ok"}
        mock_cas_class.return_value = mock_session

        # Test
        connection = SWATConnection("hostname", 5570)
        connection.connect()

        assert connection.is_healthy()
        mock_session.serverstatus.assert_called()

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_is_healthy_when_disconnected(self, mock_cas_class):
        """Test health check when session dies."""
        # Setup mock
        mock_session = Mock()
        mock_session.serverstatus.return_value = {"status": "ok"}
        mock_cas_class.return_value = mock_session

        # Connect
        connection = SWATConnection("hostname", 5570)
        connection.connect()
        assert connection.is_healthy()

        # Simulate disconnection
        mock_session.serverstatus.side_effect = Exception("Connection lost")

        # Check health
        assert not connection.is_healthy()


class TestSWATConnectionReconnect:
    """Test reconnection logic."""

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_reconnect_success(self, mock_cas_class):
        """Test successful reconnection."""
        # Setup mock
        old_session = Mock()
        old_session.serverstatus.return_value = {"status": "ok"}
        old_session.close = Mock()

        new_session = Mock()
        new_session.serverstatus.return_value = {"status": "ok"}

        mock_cas_class.side_effect = [old_session, new_session]

        # Connect
        connection = SWATConnection("hostname", 5570)
        connection.connect()
        assert connection._session == old_session

        # Reconnect
        connection.reconnect()

        # Verify old session closed and new session created
        old_session.close.assert_called_once()
        assert connection._session == new_session
        assert mock_cas_class.call_count == 2

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_reconnect_when_not_connected(self, mock_cas_class):
        """Test reconnect when no prior connection."""
        # Setup mock
        mock_session = Mock()
        mock_session.serverstatus.return_value = {"status": "ok"}
        mock_cas_class.return_value = mock_session

        # Reconnect without prior connect
        connection = SWATConnection("hostname", 5570)
        connection.reconnect()

        # Should establish new connection
        assert connection._session == mock_session
        mock_cas_class.assert_called_once()

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_reconnect_handles_close_error(self, mock_cas_class):
        """Test reconnect handles error when closing old session."""
        # Setup mock
        old_session = Mock()
        old_session.close.side_effect = Exception("Close failed")
        old_session.serverstatus.return_value = {"status": "ok"}

        new_session = Mock()
        new_session.serverstatus.return_value = {"status": "ok"}

        mock_cas_class.side_effect = [old_session, new_session]

        # Connect
        connection = SWATConnection("hostname", 5570)
        connection.connect()

        # Reconnect should succeed despite close error
        connection.reconnect()

        # Verify new session created
        assert connection._session == new_session


class TestSWATConnectionClose:
    """Test connection closing."""

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_close_success(self, mock_cas_class):
        """Test successful close."""
        # Setup mock
        mock_session = Mock()
        mock_session.serverstatus.return_value = {"status": "ok"}
        mock_session.close = Mock()
        mock_cas_class.return_value = mock_session

        # Connect and close
        connection = SWATConnection("hostname", 5570)
        connection.connect()
        connection.close()

        # Verify
        mock_session.close.assert_called_once()
        assert connection._session is None

    def test_close_when_not_connected(self):
        """Test close when not connected."""
        connection = SWATConnection("hostname", 5570)
        connection.close()  # Should not raise
        assert connection._session is None

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_close_failure(self, mock_cas_class):
        """Test close failure."""
        # Setup mock
        mock_session = Mock()
        mock_session.serverstatus.return_value = {"status": "ok"}
        mock_session.close.side_effect = Exception("Close failed")
        mock_cas_class.return_value = mock_session

        # Connect
        connection = SWATConnection("hostname", 5570)
        connection.connect()

        # Close should raise ConnectionError
        with pytest.raises(ConnectionError, match="Failed to close"):
            connection.close()

        # Session should still be cleared
        assert connection._session is None


class TestSWATConnectionGetSession:
    """Test session access."""

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_get_session_success(self, mock_cas_class):
        """Test getting session when connected."""
        # Setup mock
        mock_session = Mock()
        mock_session.serverstatus.return_value = {"status": "ok"}
        mock_cas_class.return_value = mock_session

        # Connect and get session
        connection = SWATConnection("hostname", 5570)
        connection.connect()
        session = connection.get_session()

        # Verify
        assert session == mock_session

    def test_get_session_when_not_connected(self):
        """Test getting session when not connected."""
        connection = SWATConnection("hostname", 5570)

        with pytest.raises(ConnectionError, match="Connection not established"):
            connection.get_session()

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_get_session_when_unhealthy(self, mock_cas_class):
        """Test getting session when connection is unhealthy."""
        # Setup mock
        mock_session = Mock()
        mock_session.serverstatus.return_value = {"status": "ok"}
        mock_cas_class.return_value = mock_session

        # Connect
        connection = SWATConnection("hostname", 5570)
        connection.connect()

        # Make connection unhealthy
        mock_session.serverstatus.side_effect = Exception("Connection lost")

        # Should raise error
        with pytest.raises(ConnectionError, match="Connection is not healthy"):
            connection.get_session()


class TestSWATConnectionContextManager:
    """Test context manager functionality."""

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_context_manager_connects(self, mock_cas_class):
        """Test context manager auto-connects."""
        # Setup mock
        mock_session = Mock()
        mock_session.serverstatus.return_value = {"status": "ok"}
        mock_cas_class.return_value = mock_session

        # Use context manager
        connection = SWATConnection("hostname", 5570)

        with connection as conn:
            assert conn._session == mock_session
            assert conn.is_healthy()

        # Connection should remain open after exit
        assert connection._session == mock_session

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_context_manager_reconnects_if_unhealthy(self, mock_cas_class):
        """Test context manager reconnects if needed."""
        # Setup mocks
        old_session = Mock()
        old_session.serverstatus.return_value = {"status": "ok"}
        old_session.close = Mock()

        new_session = Mock()
        new_session.serverstatus.return_value = {"status": "ok"}

        mock_cas_class.side_effect = [old_session, new_session]

        # Connect initially
        connection = SWATConnection("hostname", 5570)
        connection.connect()

        # Make connection unhealthy
        old_session.serverstatus.side_effect = Exception("Connection lost")

        # Use context manager - should reconnect
        with connection as conn:
            assert conn._session == new_session

        # Old session should be closed
        old_session.close.assert_called_once()

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_context_manager_reuses_healthy_connection(self, mock_cas_class):
        """Test context manager reuses healthy connection."""
        # Setup mock
        mock_session = Mock()
        mock_session.serverstatus.return_value = {"status": "ok"}
        mock_cas_class.return_value = mock_session

        # Connect
        connection = SWATConnection("hostname", 5570)
        connection.connect()

        # Use context manager multiple times
        with connection:
            pass

        with connection:
            pass

        # Should only create session once
        mock_cas_class.assert_called_once()

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_context_manager_propagates_exceptions(self, mock_cas_class):
        """Test context manager propagates exceptions."""
        # Setup mock
        mock_session = Mock()
        mock_session.serverstatus.return_value = {"status": "ok"}
        mock_cas_class.return_value = mock_session

        # Test exception propagation
        connection = SWATConnection("hostname", 5570)

        with pytest.raises(RuntimeError, match="Test error"):
            with connection:
                raise RuntimeError("Test error")


class TestSWATConnectionGetOperation:
    """Test operation adapter factory method."""

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    @patch("sas_model_kit.operation.swat.isinstance")
    def test_get_operation_success(self, mock_isinstance, mock_cas_class):
        """Test getting operation adapter when connected."""
        # Setup mocks
        mock_session = Mock()
        mock_session.serverstatus.return_value = {"status": "ok"}
        mock_cas_class.return_value = mock_session
        mock_isinstance.return_value = True  # Make isinstance check pass

        # Connect and get operation
        connection = SWATConnection("hostname", 5570)
        connection.connect()
        operation = connection.get_operation()

        # Verify operation adapter is created
        from sas_model_kit.operation.swat import SWATOperationAdapter

        assert isinstance(operation, SWATOperationAdapter)
        assert operation._session is mock_session

    def test_get_operation_when_not_connected(self):
        """Test getting operation when not connected."""
        connection = SWATConnection("hostname", 5570)

        with pytest.raises(ConnectionError, match="Connection not established"):
            connection.get_operation()

    @patch("sas_model_kit.connection.swat.connection.swat.CAS")
    def test_get_operation_when_unhealthy(self, mock_cas_class):
        """Test getting operation when connection is unhealthy."""
        # Setup mock
        mock_session = Mock()
        mock_session.serverstatus.return_value = {"status": "ok"}
        mock_cas_class.return_value = mock_session

        # Connect
        connection = SWATConnection("hostname", 5570)
        connection.connect()

        # Make connection unhealthy
        mock_session.serverstatus.side_effect = Exception("Connection lost")

        # Should raise error
        with pytest.raises(ConnectionError, match="Connection is not healthy"):
            connection.get_operation()
