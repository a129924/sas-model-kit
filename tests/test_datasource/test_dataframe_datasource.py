"""
Unit tests for DataFrameDataSource.

Tests the pandas DataFrame data source implementation, verifying:
- Initialization with valid/invalid data
- Data preparation (upload) via prepare()
- Result fetching via fetch_result()
- Error handling and edge cases
"""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from sas_model_kit.datasource.dataframe import DataFrameDataSource
from sas_model_kit.error import DataFetchFailure, OperationError, UploadFailure
from sas_model_kit.result import Err, Ok


class TestDataFrameDataSourceInit:
    """Test DataFrameDataSource initialization."""

    def test_init_with_valid_dataframe(self):
        """Should initialize successfully with valid DataFrame."""
        # Arrange
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

        # Act
        datasource = DataFrameDataSource(df, "public", "my_data")

        # Assert
        assert datasource._data is df
        assert datasource._caslib == "public"
        assert datasource._table == "my_data"

    def test_init_with_non_dataframe(self):
        """Should raise TypeError with non-DataFrame data."""
        # Arrange
        invalid_data = {"a": [1, 2], "b": [3, 4]}  # dict, not DataFrame

        # Act & Assert
        with pytest.raises(TypeError) as exc_info:
            DataFrameDataSource(invalid_data, "public", "data")  # type: ignore

        assert "Expected pandas DataFrame" in str(exc_info.value)
        assert "got dict" in str(exc_info.value)

    def test_init_with_empty_caslib(self):
        """Should raise ValueError with empty caslib."""
        # Arrange
        df = pd.DataFrame({"a": [1, 2]})

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            DataFrameDataSource(df, "", "data")

        assert "caslib cannot be empty" in str(exc_info.value)

    def test_init_with_empty_table(self):
        """Should raise ValueError with empty table."""
        # Arrange
        df = pd.DataFrame({"a": [1, 2]})

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            DataFrameDataSource(df, "public", "")

        assert "table cannot be empty" in str(exc_info.value)

    def test_init_with_whitespace_only_caslib(self):
        """Should raise ValueError with whitespace-only caslib."""
        # Arrange
        df = pd.DataFrame({"a": [1, 2]})

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            DataFrameDataSource(df, "   ", "data")

        assert "caslib cannot be empty" in str(exc_info.value)


class TestDataFrameDataSourcePrepare:
    """Test DataFrameDataSource.prepare() method."""

    def test_prepare_successful(self):
        """Should upload DataFrame successfully."""
        # Arrange
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        datasource = DataFrameDataSource(df, "public", "my_data")

        mock_operation = MagicMock()
        mock_operation.upload_data = MagicMock(return_value=Ok("uploaded"))

        # Act
        result = datasource.prepare(mock_operation)

        # Assert
        mock_operation.upload_data.assert_called_once_with(
            df, caslib="public", table="my_data"
        )
        assert result.is_ok
        assert result.value is None

    def test_prepare_with_upload_failure(self):
        """Should raise RuntimeError when upload fails."""
        # Arrange
        df = pd.DataFrame({"a": [1, 2]})
        datasource = DataFrameDataSource(df, "public", "data")

        mock_operation = MagicMock()
        mock_operation.upload_data = MagicMock(
            return_value=Err(
                OperationError(code="UPLOAD_FAILED", message="upload failed")
            )
        )

        # Act
        result = datasource.prepare(mock_operation)

        # Assert
        assert result.is_err
        assert isinstance(result.error, UploadFailure)


class TestDataFrameDataSourceFetchResult:
    """Test DataFrameDataSource.fetch_result() method."""

    def test_fetch_result_successful(self):
        """Should fetch DataFrame results successfully."""
        # Arrange
        df = pd.DataFrame({"a": [1, 2]})
        datasource = DataFrameDataSource(df, "public", "input")

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
        df = pd.DataFrame({"a": [1, 2]})
        datasource = DataFrameDataSource(df, "public", "input")

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
        df = pd.DataFrame({"a": [1, 2]})
        datasource = DataFrameDataSource(df, "public", "input")

        # Mock result with non-DataFrame in 'Fetch'
        mock_result = {"Fetch": "not a dataframe"}
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
        df = pd.DataFrame({"a": [1, 2]})
        datasource = DataFrameDataSource(df, "public", "input")

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
