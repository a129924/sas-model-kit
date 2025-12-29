"""
Unit tests for SWATOperationAdapter.

Tests the SWAT-specific operation adapter implementation, verifying:
- Initialization with valid/invalid sessions
- Action execution via call_action()
- Data upload via upload_data()
- Error handling and edge cases
"""

from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from sas_model_kit.operation.swat import SWATOperationAdapter


class TestSWATOperationAdapterInit:
    """Test SWATOperationAdapter initialization."""

    def test_init_with_valid_session(self):
        """Should initialize successfully with valid swat.CAS session."""
        # Arrange
        mock_session = MagicMock(spec=['__class__'])
        mock_session.__class__.__name__ = 'CAS'
        mock_session.__class__.__module__ = 'swat'

        # Patch isinstance to return True for our mock
        with patch('sas_model_kit.operation.swat.isinstance', return_value=True):
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
            SWATOperationAdapter(invalid_session)

        assert "SWATOperationAdapter requires a swat.CAS connection" in str(exc_info.value)
        assert "got str" in str(exc_info.value)
