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

        # Mock result indicating table exists
        mock_result = {"exists": 1}
        mock_operation = MagicMock()
        mock_operation.call_action = MagicMock(return_value=mock_result)

        # Act (should not raise)
        datasource.prepare(mock_operation)

        # Assert
        mock_operation.call_action.assert_called_once_with(
            "table.tableExists", caslib="public", name="existing_data"
        )

    def test_prepare_with_nonexistent_table(self):
        """Should raise ValueError when table doesn't exist."""
        # Arrange
        datasource = CASTableDataSource("public", "missing_data")

        # Mock result indicating table doesn't exist
        mock_result = {"exists": 0}
        mock_operation = MagicMock()
        mock_operation.call_action = MagicMock(return_value=mock_result)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            datasource.prepare(mock_operation)

        assert "Table public.missing_data does not exist" in str(exc_info.value)

    def test_prepare_with_unexpected_result_format(self):
        """Should raise ValueError with unexpected result format."""
        # Arrange
        datasource = CASTableDataSource("public", "data")

        # Mock result with unexpected format (not a dict-like object)
        mock_result = "unexpected format"
        mock_operation = MagicMock()
        mock_operation.call_action = MagicMock(return_value=mock_result)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            datasource.prepare(mock_operation)

        assert "Unexpected result format from table.tableExists" in str(exc_info.value)

    def test_prepare_with_action_failure(self):
        """Should raise RuntimeError when tableExists action fails."""
        # Arrange
        datasource = CASTableDataSource("public", "data")

        mock_operation = MagicMock()
        mock_operation.call_action = MagicMock(
            side_effect=RuntimeError("action failed")
        )

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            datasource.prepare(mock_operation)

        assert "Failed to validate CAS table public.data" in str(exc_info.value)


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
        mock_operation.call_action = MagicMock(return_value=mock_result)

        # Act
        result = datasource.fetch_result(
            mock_operation, caslib="public", table="output"
        )

        # Assert
        mock_operation.call_action.assert_called_once_with(
            "table.fetch", table={"name": "output", "caslib": "public"}
        )
        assert isinstance(result, pd.DataFrame)
        assert result is result_df

    def test_fetch_result_with_missing_fetch_key(self):
        """Should raise ValueError when result has no 'Fetch' key."""
        # Arrange
        datasource = CASTableDataSource("public", "input")

        # Mock result without 'Fetch' key
        mock_result = {"SomeOtherKey": "value"}
        mock_operation = MagicMock()
        mock_operation.call_action = MagicMock(return_value=mock_result)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            datasource.fetch_result(mock_operation, "public", "output")

        assert "Unexpected result format from table.fetch" in str(exc_info.value)

    def test_fetch_result_with_non_dataframe_value(self):
        """Should raise ValueError when 'Fetch' value is not DataFrame."""
        # Arrange
        datasource = CASTableDataSource("public", "input")

        # Mock result with non-DataFrame in 'Fetch'
        mock_result = {"Fetch": [1, 2, 3]}  # list, not DataFrame
        mock_operation = MagicMock()
        mock_operation.call_action = MagicMock(return_value=mock_result)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            datasource.fetch_result(mock_operation, "public", "output")

        assert "Expected DataFrame from fetch" in str(exc_info.value)
        assert "got list" in str(exc_info.value)

    def test_fetch_result_with_action_failure(self):
        """Should raise RuntimeError when table.fetch fails."""
        # Arrange
        datasource = CASTableDataSource("public", "input")

        mock_operation = MagicMock()
        mock_operation.call_action = MagicMock(side_effect=RuntimeError("fetch failed"))

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            datasource.fetch_result(mock_operation, "public", "output")

        assert "Failed to fetch result from public.output" in str(exc_info.value)


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
