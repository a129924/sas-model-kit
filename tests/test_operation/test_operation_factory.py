"""
Unit tests for OperationFactory.

Tests the factory method pattern for creating operation adapters,
verifying:
- Correct adapter creation for each connection type
- Error handling for unsupported types
- Connection health checks before creation
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from sas_model_kit.connection.base import ConnectionType
from sas_model_kit.operation.factory import OperationFactory
from sas_model_kit.operation.swat import SWATOperationAdapter


class TestOperationFactoryCreate:
    """Test OperationFactory.create() method."""

    @patch("sas_model_kit.operation.swat.isinstance")
    def test_create_swat_adapter(self, mock_isinstance):
        """Should create SWATOperationAdapter for SWAT connection."""
        # Arrange
        mock_connection = MagicMock()
        mock_connection.connection_type = ConnectionType.SWAT
        mock_session = MagicMock()
        mock_connection.get_session.return_value = mock_session
        mock_isinstance.return_value = True  # Make isinstance check pass

        # Act
        operation = OperationFactory.create(mock_connection)

        # Assert
        assert isinstance(operation, SWATOperationAdapter)
        assert operation._session is mock_session
        mock_connection.get_session.assert_called_once()

    def test_create_with_sasctl_not_implemented(self):
        """Should raise NotImplementedError for SASCTL connection."""
        # Arrange
        mock_connection = MagicMock()
        mock_connection.connection_type = ConnectionType.SASCTL
        mock_session = MagicMock()
        mock_connection.get_session.return_value = mock_session

        # Act & Assert
        with pytest.raises(NotImplementedError) as exc_info:
            OperationFactory.create(mock_connection)

        assert "SASCTL operation adapter not yet implemented" in str(exc_info.value)

    def test_create_with_httpx_not_implemented(self):
        """Should raise NotImplementedError for HTTPx connection."""
        # Arrange
        mock_connection = MagicMock()
        mock_connection.connection_type = ConnectionType.HTTPX
        mock_session = MagicMock()
        mock_connection.get_session.return_value = mock_session

        # Act & Assert
        with pytest.raises(NotImplementedError) as exc_info:
            OperationFactory.create(mock_connection)

        assert "HTTPx operation adapter not yet implemented" in str(exc_info.value)

    def test_create_with_invalid_connection_type(self):
        """Should raise ValueError for unknown connection type."""
        # Arrange
        mock_connection = MagicMock()
        mock_connection.connection_type = "INVALID"  # Invalid type
        mock_session = MagicMock()
        mock_connection.get_session.return_value = mock_session

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            OperationFactory.create(mock_connection)

        assert "Unsupported connection type" in str(exc_info.value)

    def test_create_with_unhealthy_connection(self):
        """Should raise ConnectionError if get_session() fails."""
        # Arrange
        mock_connection = MagicMock()
        mock_connection.connection_type = ConnectionType.SWAT
        mock_connection.get_session.side_effect = ConnectionError(
            "Connection not healthy"
        )

        # Act & Assert
        with pytest.raises(ConnectionError) as exc_info:
            OperationFactory.create(mock_connection)

        assert "Connection not healthy" in str(exc_info.value)
        mock_connection.get_session.assert_called_once()
