"""
Unit tests for CASTableDataSource.

Tests the CAS table data source implementation, verifying:
- Initialization with valid/invalid parameters
- Table validation via prepare()
- Result fetching via fetch_result()
- Property accessors
- Error handling and edge cases
"""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from sas_model_kit.datasource.cas_table import CASTableDataSource
from sas_model_kit.error import DataFetchFailure, OperationError, UploadFailure
from sas_model_kit.result import Err, Ok


class TestCASTableDataSourceInit:
    """Test CASTableDataSource initialization."""

    def test_init_with_valid_parameters(self):
        """Should initialize successfully with valid caslib and table."""
        # Act
        datasource = CASTableDataSource("public", "my_data")

        # Assert
        assert datasource._caslib == "public"
        assert datasource._table == "my_data"
        assert datasource.caslib == "public"
        assert datasource.table == "my_data"

    def test_init_with_empty_caslib(self):
        """Should raise ValueError with empty caslib."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            CASTableDataSource("", "data")

        assert "caslib cannot be empty" in str(exc_info.value)

    def test_init_with_empty_table(self):
        """Should raise ValueError with empty table."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            CASTableDataSource("public", "")

        assert "table cannot be empty" in str(exc_info.value)

    def test_init_with_whitespace_only_table(self):
        """Should raise ValueError with whitespace-only table."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            CASTableDataSource("public", "   ")

        assert "table cannot be empty" in str(exc_info.value)


class TestCASTableDataSourcePrepare:
    """Test CASTableDataSource.prepare() method."""

    def test_prepare_with_existing_table(self):
        """Should validate successfully when table exists."""
        # Arrange
        datasource = CASTableDataSource("public", "existing_data")

        # Mock operation.table_exists to return True
        mock_operation = MagicMock()
        mock_operation.table_exists = MagicMock(return_value=Ok(True))

        # Act
        result = datasource.prepare(mock_operation)

        # Assert
        mock_operation.table_exists.assert_called_once_with("public", "existing_data")
        assert result.is_ok
        assert result.value is None

    def test_prepare_with_nonexistent_table(self):
        """Should fail when table doesn't exist."""
        # Arrange
        datasource = CASTableDataSource("public", "missing_data")

        # Mock operation.table_exists to return False
        mock_operation = MagicMock()
        mock_operation.table_exists = MagicMock(return_value=Ok(False))

        # Act
        result = datasource.prepare(mock_operation)

        # Assert
        assert result.is_err
        assert isinstance(result.error, UploadFailure)
        assert "TABLE_NOT_FOUND" in result.error.code

    def test_prepare_with_operation_error(self):
        """Should propagate OperationError as UploadFailure."""
        # Arrange
        datasource = CASTableDataSource("public", "data")

        # Mock operation.table_exists to return OperationError
        mock_operation = MagicMock()
        mock_operation.table_exists = MagicMock(
            return_value=Err(
                OperationError(
                    code="TABLE_CHECK_FAILED", message="Failed to check table"
                )
            )
        )

        # Act
        result = datasource.prepare(mock_operation)

        # Assert
        assert result.is_err
        assert isinstance(result.error, UploadFailure)

    def test_prepare_preserves_operation_error_context(self):
        """Should preserve OperationError context when converting to UploadFailure."""
        # Arrange
        datasource = CASTableDataSource("public", "data")

        mock_operation = MagicMock()
        op_error = OperationError(
            code="ACTION_FAILED",
            message="action failed",
            severity="ERROR",
            context={"details": "test error"},
        )
        mock_operation.table_exists = MagicMock(return_value=Err(op_error))

        # Act
        result = datasource.prepare(mock_operation)

        # Assert
        assert result.is_err
        assert isinstance(result.error, UploadFailure)
        assert result.error.code == "ACTION_FAILED"
        assert result.error.message == "action failed"


class TestCASTableDataSourceFetchResult:
    """Test CASTableDataSource.fetch_result() method."""

    def test_fetch_result_successful(self):
        """Should fetch DataFrame results successfully."""
        # Arrange
        datasource = CASTableDataSource("public", "input")

        # Create mock result with DataFrame in 'Fetch' key
        result_df = pd.DataFrame({"score": [0.9, 0.8]})
        mock_result = {"Fetch": result_df}

        mock_operation = MagicMock()
        mock_operation.call_action = MagicMock(return_value=Ok(mock_result))

        # Act
        result = datasource.fetch_result(
            mock_operation, caslib="public", table="output"
        )

        # Assert
        mock_operation.call_action.assert_called_once_with(
            "table.fetch", table={"name": "output", "caslib": "public"}
        )
        assert result.is_ok
        assert isinstance(result.value, pd.DataFrame)
        assert result.value is result_df

    def test_fetch_result_with_missing_fetch_key(self):
        """Should raise ValueError when result has no 'Fetch' key."""
        # Arrange
        datasource = CASTableDataSource("public", "input")

        # Mock result without 'Fetch' key
        mock_result = {"SomeOtherKey": "value"}
        mock_operation = MagicMock()
        mock_operation.call_action = MagicMock(return_value=Ok(mock_result))

        # Act
        result = datasource.fetch_result(mock_operation, "public", "output")

        # Assert
        assert result.is_err
        assert isinstance(result.error, DataFetchFailure)

    def test_fetch_result_with_non_dataframe_value(self):
        """Should raise ValueError when 'Fetch' value is not DataFrame."""
        # Arrange
        datasource = CASTableDataSource("public", "input")

        # Mock result with non-DataFrame in 'Fetch'
        mock_result = {"Fetch": [1, 2, 3]}  # list, not DataFrame
        mock_operation = MagicMock()
        mock_operation.call_action = MagicMock(return_value=Ok(mock_result))

        # Act
        result = datasource.fetch_result(mock_operation, "public", "output")

        # Assert
        assert result.is_err
        assert isinstance(result.error, DataFetchFailure)

    def test_fetch_result_with_action_failure(self):
        """Should raise RuntimeError when table.fetch fails."""
        # Arrange
        datasource = CASTableDataSource("public", "input")

        mock_operation = MagicMock()
        mock_operation.call_action = MagicMock(
            return_value=Err(
                OperationError(code="FETCH_FAILED", message="fetch failed")
            )
        )

        # Act
        result = datasource.fetch_result(mock_operation, "public", "output")

        # Assert
        assert result.is_err
        assert isinstance(result.error, DataFetchFailure)


class TestCASTableDataSourceProperties:
    """Test CASTableDataSource property accessors."""

    def test_caslib_property(self):
        """Should return correct caslib value."""
        # Arrange
        datasource = CASTableDataSource("my_caslib", "my_table")

        # Act & Assert
        assert datasource.caslib == "my_caslib"

    def test_table_property(self):
        """Should return correct table value."""
        # Arrange
        datasource = CASTableDataSource("my_caslib", "my_table")

        # Act & Assert
        assert datasource.table == "my_table"
