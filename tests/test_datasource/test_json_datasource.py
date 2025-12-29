"""
Unit tests for JSONDataSource.

Tests the JSON data source implementation, verifying:
- Initialization with valid/invalid data
- Data preparation (upload) via prepare()
- Result fetching as dictionary via fetch_result()
- Error handling and edge cases
"""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from sas_model_kit.datasource.json import JSONDataSource


class TestJSONDataSourceInit:
    """Test JSONDataSource initialization."""

    def test_init_with_dataframe(self):
        """Should initialize successfully with DataFrame."""
        # Arrange
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

        # Act
        datasource = JSONDataSource(df, "public", "my_data")

        # Assert
        assert datasource._data is df
        assert datasource._caslib == "public"
        assert datasource._table == "my_data"

    def test_init_with_dict(self):
        """Should initialize successfully with dict."""
        # Arrange
        data = {"a": [1, 2], "b": [3, 4]}

        # Act
        datasource = JSONDataSource(data, "public", "my_data")

        # Assert
        assert datasource._data is data
        assert datasource._caslib == "public"
        assert datasource._table == "my_data"

    def test_init_with_invalid_type(self):
        """Should raise TypeError with unsupported data type."""
        # Arrange
        invalid_data = [1, 2, 3]  # list is not supported

        # Act & Assert
        with pytest.raises(TypeError) as exc_info:
            JSONDataSource(invalid_data, "public", "data")

        assert "Expected DataFrame or dict" in str(exc_info.value)
        assert "got list" in str(exc_info.value)

    def test_init_with_empty_caslib(self):
        """Should raise ValueError with empty caslib."""
        # Arrange
        data = {"a": [1, 2]}

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            JSONDataSource(data, "", "data")

        assert "caslib cannot be empty" in str(exc_info.value)

    def test_init_with_empty_table(self):
        """Should raise ValueError with empty table."""
        # Arrange
        data = {"a": [1, 2]}

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            JSONDataSource(data, "public", "")

        assert "table cannot be empty" in str(exc_info.value)


class TestJSONDataSourcePrepare:
    """Test JSONDataSource.prepare() method."""

    def test_prepare_with_dataframe(self):
        """Should upload DataFrame successfully."""
        # Arrange
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        datasource = JSONDataSource(df, "public", "my_data")

        mock_operation = MagicMock()
        mock_operation.upload_data = MagicMock()

        # Act
        datasource.prepare(mock_operation)

        # Assert
        mock_operation.upload_data.assert_called_once_with(
            df, caslib="public", table="my_data"
        )

    def test_prepare_with_dict(self):
        """Should convert dict to DataFrame and upload."""
        # Arrange
        data = {"a": [1, 2], "b": [3, 4]}
        datasource = JSONDataSource(data, "public", "my_data")

        mock_operation = MagicMock()
        mock_operation.upload_data = MagicMock()

        # Act
        datasource.prepare(mock_operation)

        # Assert
        mock_operation.upload_data.assert_called_once()
        call_args = mock_operation.upload_data.call_args

        # Verify uploaded data is a DataFrame
        uploaded_data = call_args[0][0]
        assert isinstance(uploaded_data, pd.DataFrame)
        assert list(uploaded_data.columns) == ["a", "b"]
        assert uploaded_data["a"].tolist() == [1, 2]
        assert uploaded_data["b"].tolist() == [3, 4]

        # Verify caslib and table
        assert call_args[1]["caslib"] == "public"
        assert call_args[1]["table"] == "my_data"

    def test_prepare_with_upload_failure(self):
        """Should raise RuntimeError when upload fails."""
        # Arrange
        df = pd.DataFrame({"a": [1, 2]})
        datasource = JSONDataSource(df, "public", "data")

        mock_operation = MagicMock()
        mock_operation.upload_data = MagicMock(
            side_effect=RuntimeError("upload failed")
        )

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            datasource.prepare(mock_operation)

        assert "Failed to prepare JSON data source" in str(exc_info.value)


class TestJSONDataSourceFetchResult:
    """Test JSONDataSource.fetch_result() method."""

    def test_fetch_result_successful(self):
        """Should fetch results as dictionary successfully."""
        # Arrange
        df = pd.DataFrame({"a": [1, 2]})
        datasource = JSONDataSource(df, "public", "input")

        # Create mock result with DataFrame in 'Fetch' key
        result_df = pd.DataFrame({"score": [0.9, 0.8], "label": ["A", "B"]})
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
        assert isinstance(result, dict)
        assert result == {"score": [0.9, 0.8], "label": ["A", "B"]}

    def test_fetch_result_with_missing_fetch_key(self):
        """Should raise ValueError when result has no 'Fetch' key."""
        # Arrange
        df = pd.DataFrame({"a": [1, 2]})
        datasource = JSONDataSource(df, "public", "input")

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
        df = pd.DataFrame({"a": [1, 2]})
        datasource = JSONDataSource(df, "public", "input")

        # Mock result with non-DataFrame in 'Fetch'
        mock_result = {"Fetch": {"key": "value"}}  # dict, not DataFrame
        mock_operation = MagicMock()
        mock_operation.call_action = MagicMock(return_value=mock_result)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            datasource.fetch_result(mock_operation, "public", "output")

        assert "Expected DataFrame from fetch" in str(exc_info.value)
        assert "got dict" in str(exc_info.value)

    def test_fetch_result_with_action_failure(self):
        """Should raise RuntimeError when table.fetch fails."""
        # Arrange
        df = pd.DataFrame({"a": [1, 2]})
        datasource = JSONDataSource(df, "public", "input")

        mock_operation = MagicMock()
        mock_operation.call_action = MagicMock(side_effect=RuntimeError("fetch failed"))

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            datasource.fetch_result(mock_operation, "public", "output")

        assert "Failed to fetch result from public.output" in str(exc_info.value)
