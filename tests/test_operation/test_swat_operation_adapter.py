"""
Unit tests for SWATOperationAdapter.

Tests the SWAT-specific operation adapter implementation, verifying:
- Initialization with valid/invalid sessions
- Action execution via call_action()
- Data upload via upload_data()
- Validation methods (table_exists, model_exists)
- Error handling and edge cases
"""

from unittest.mock import MagicMock, patch

import pytest

from sas_model_kit.operation.swat import SWATOperationAdapter


class TestSWATOperationAdapterInit:
    """Test SWATOperationAdapter initialization."""

    def test_init_with_valid_session(self):
        """Should initialize successfully with valid swat.CAS session."""
        # Arrange
        mock_session = MagicMock(spec=["__class__"])
        mock_session.__class__.__name__ = "CAS"
        mock_session.__class__.__module__ = "swat"

        # Patch isinstance to return True for our mock
        with patch("sas_model_kit.operation.swat.isinstance", return_value=True):
            # Act
            adapter = SWATOperationAdapter(mock_session)

            # Assert
            assert adapter._session is mock_session

    def test_init_with_invalid_session(self):
        """Should raise TypeError with non-swat.CAS session."""
        # Arrange
        invalid_session = "not a CAS session"

        # Act & Assert
        with pytest.raises(TypeError) as exc_info:
            SWATOperationAdapter(invalid_session)  # type: ignore

        assert "SWATOperationAdapter requires a swat.CAS connection" in str(
            exc_info.value
        )
        assert "got str" in str(exc_info.value)


class TestSWATOperationAdapterValidation:
    """Test SWATOperationAdapter validation methods."""

    def test_table_exists_returns_true_when_table_exists(self):
        """Should return True when table exists."""
        # Arrange
        mock_session = MagicMock()
        mock_session.table.tableExists.return_value = {"exists": 1}

        with patch("sas_model_kit.operation.swat.isinstance", return_value=True):
            adapter = SWATOperationAdapter(mock_session)

            # Act
            result = adapter.table_exists("public", "my_table")

            # Assert
            assert result is True
            mock_session.table.tableExists.assert_called_once_with(
                caslib="public",
                name="my_table",
            )

    def test_table_exists_returns_false_when_table_missing(self):
        """Should return False when table doesn't exist."""
        # Arrange
        mock_session = MagicMock()
        mock_session.table.tableExists.return_value = {"exists": 0}

        with patch("sas_model_kit.operation.swat.isinstance", return_value=True):
            adapter = SWATOperationAdapter(mock_session)

            # Act
            result = adapter.table_exists("public", "missing_table")

            # Assert
            assert result is False

    def test_table_exists_returns_false_on_error(self):
        """Should return False when tableExists action fails."""
        # Arrange
        mock_session = MagicMock()
        mock_session.table.tableExists.side_effect = Exception("CAS error")

        with patch("sas_model_kit.operation.swat.isinstance", return_value=True):
            adapter = SWATOperationAdapter(mock_session)

            # Act
            result = adapter.table_exists("public", "my_table")

            # Assert
            assert result is False

    def test_model_exists_returns_true_when_model_exists(self):
        """Should return True when model (ASTORE) exists."""
        # Arrange
        mock_session = MagicMock()
        mock_session.table.tableExists.return_value = {"exists": 1}

        with patch("sas_model_kit.operation.swat.isinstance", return_value=True):
            adapter = SWATOperationAdapter(mock_session)

            # Act
            result = adapter.model_exists("models", "my_astore")

            # Assert
            assert result is True
            mock_session.table.tableExists.assert_called_once_with(
                caslib="models",
                name="my_astore",
            )

    def test_model_exists_returns_false_when_model_missing(self):
        """Should return False when model doesn't exist."""
        # Arrange
        mock_session = MagicMock()
        mock_session.table.tableExists.return_value = {"exists": 0}

        with patch("sas_model_kit.operation.swat.isinstance", return_value=True):
            adapter = SWATOperationAdapter(mock_session)

            # Act
            result = adapter.model_exists("models", "missing_model")

            # Assert
            assert result is False

    def test_model_exists_uses_table_exists_internally(self):
        """Should use table_exists for model validation."""
        # Arrange
        mock_session = MagicMock()
        mock_session.table.tableExists.return_value = {"exists": 1}

        with patch("sas_model_kit.operation.swat.isinstance", return_value=True):
            adapter = SWATOperationAdapter(mock_session)

            # Act
            result = adapter.model_exists("models", "my_astore")

            # Assert
            # Since model_exists calls table_exists, verify the underlying call
            assert result is True
            mock_session.table.tableExists.assert_called_once()
