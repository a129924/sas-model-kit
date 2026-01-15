"""Tests for SWATOperationsImpl implementing all 8 Able Protocols."""

from unittest.mock import MagicMock, Mock, PropertyMock

import pytest

from sas_model_kit.error import OperationError, OperationErrorCode, TableNotFoundError
from sas_model_kit.helpers.swat.operations import SWATOperationsImpl
from sas_model_kit.result import Err, Ok


class TestSWATOperationsImplReadAble:
    """Test ReadAble protocol implementation."""

    def test_get_columns_success(self):
        """Should return list of column names."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        table = Mock()
        table.columns = ["col1", "col2", "col3"]

        # Act
        result = ops.get_columns(table)

        # Assert
        assert result.is_ok
        assert result.value == ["col1", "col2", "col3"]

    def test_get_columns_error(self):
        """Should return OperationError when reading columns fails."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        table = Mock()
        original_error = ValueError("Invalid table")
        type(table).columns = PropertyMock(side_effect=original_error)

        # Act
        result = ops.get_columns(table)

        # Assert
        assert result.is_err
        assert isinstance(result.error, OperationError)
        assert result.error.code == OperationErrorCode.READ_FAILED
        assert "Failed to get columns" in result.error.message
        assert result.error.__cause__ is original_error

    def test_get_table_location_success(self):
        """Should return (caslib, table_name) tuple."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        table = Mock()
        table.params = {"caslib": "mycaslib", "name": "mytable"}

        # Act
        result = ops.get_table_location(table)

        # Assert
        assert result.is_ok
        assert result.value == ("mycaslib", "mytable")

    def test_get_table_location_default_caslib(self):
        """Should default to 'public' caslib if not specified."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        table = Mock()
        table.params = {"name": "mytable"}

        # Act
        result = ops.get_table_location(table)

        # Assert
        assert result.is_ok
        assert result.value == ("public", "mytable")

    def test_get_table_location_missing_name_error(self):
        """Should return error if table name is missing."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        table = Mock()
        table.params = {"caslib": "mycaslib"}

        # Act
        result = ops.get_table_location(table)

        # Assert
        assert result.is_err
        assert isinstance(result.error, OperationError)
        assert result.error.code == OperationErrorCode.READ_FAILED


class TestSWATOperationsImplWriteAble:
    """Test WriteAble protocol implementation."""

    def test_create_table_success(self):
        """Should create table and return CASTable reference."""
        # Arrange
        operation = Mock()
        operation.upload_data = Mock(return_value=Ok(None))
        operation._session = Mock()
        mock_table = Mock()
        operation._session.CASTable = Mock(return_value=mock_table)

        ops = SWATOperationsImpl(operation)
        source_data = Mock()

        # Act
        result = ops.create_table(
            name="newtable",
            caslib="mycaslib",
            source=source_data,
            replace=True,
        )

        # Assert
        assert result.is_ok
        assert result.value is mock_table
        operation.upload_data.assert_called_once_with(
            data=source_data,
            caslib="mycaslib",
            table="newtable",
            replace=True,
        )
        operation._session.CASTable.assert_called_once_with(
            name="newtable",
            caslib="mycaslib",
        )

    def test_create_table_upload_fails(self):
        """Should return error when upload_data fails."""
        # Arrange
        operation = Mock()
        upload_error = OperationError(
            code=OperationErrorCode.WRITE_FAILED,
            message="Upload failed",
        )
        operation.upload_data = Mock(return_value=Err(upload_error))

        ops = SWATOperationsImpl(operation)
        source_data = Mock()

        # Act
        result = ops.create_table(
            name="newtable",
            caslib="mycaslib",
            source=source_data,
        )

        # Assert
        assert result.is_err
        assert isinstance(result.error, OperationError)
        assert result.error.code == OperationErrorCode.WRITE_FAILED
        assert "Failed to upload data for table 'newtable'" in result.error.message

    def test_create_table_exception(self):
        """Should handle exceptions during table creation."""
        # Arrange
        operation = Mock()
        operation.upload_data = Mock(side_effect=RuntimeError("Unexpected error"))

        ops = SWATOperationsImpl(operation)

        # Act
        result = ops.create_table(
            name="newtable",
            caslib="mycaslib",
            source=Mock(),
        )

        # Assert
        assert result.is_err
        assert isinstance(result.error, OperationError)
        assert result.error.code == OperationErrorCode.WRITE_FAILED


class TestSWATOperationsImplSortAble:
    """Test SortAble protocol implementation."""

    def test_sort_values_single_column_ascending(self):
        """Should sort table by single column in ascending order."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        table = Mock()
        sorted_table = Mock()
        table.sort_values = Mock(return_value=sorted_table)

        # Act
        result = ops.sort_values(table, by=["col1"], ascending=True)

        # Assert
        assert result.is_ok
        assert result.value is sorted_table
        table.sort_values.assert_called_once_with(by=["col1"], ascending=True)

    def test_sort_values_multiple_columns(self):
        """Should sort by multiple columns with different orders."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        table = Mock()
        sorted_table = Mock()
        table.sort_values = Mock(return_value=sorted_table)

        # Act
        result = ops.sort_values(table, by=["col1", "col2"], ascending=[True, False])

        # Assert
        assert result.is_ok
        table.sort_values.assert_called_once_with(
            by=["col1", "col2"],
            ascending=[True, False],
        )

    def test_sort_values_error(self):
        """Should return error when sort fails."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        table = Mock()
        sort_error = ValueError("Invalid column")
        table.sort_values = Mock(side_effect=sort_error)

        # Act
        result = ops.sort_values(table, by=["invalid_col"])

        # Assert
        assert result.is_err
        assert isinstance(result.error, OperationError)
        assert result.error.code == OperationErrorCode.SORT_FAILED
        assert result.error.__cause__ is sort_error


class TestSWATOperationsImplDeleteAble:
    """Test DeleteAble protocol implementation."""

    def test_drop_table_success(self):
        """Should drop table successfully."""
        # Arrange
        operation = Mock()
        operation.call_action = Mock(return_value=Ok({"status": "OK"}))
        ops = SWATOperationsImpl(operation)

        # Act
        result = ops.drop_table(caslib="mycaslib", table="mytable")

        # Assert
        assert result.is_ok
        assert result.value is None
        operation.call_action.assert_called_once_with(
            "table.dropTable",
            caslib="mycaslib",
            name="mytable",
        )

    def test_drop_table_error(self):
        """Should return error when drop fails."""
        # Arrange
        operation = Mock()
        drop_error = OperationError(
            code=OperationErrorCode.SWAT_EXECUTION_ERROR,
            message="Table not found",
        )
        operation.call_action = Mock(return_value=Err(drop_error))
        ops = SWATOperationsImpl(operation)

        # Act
        result = ops.drop_table(caslib="mycaslib", table="mytable")

        # Assert
        assert result.is_err
        assert result.error is drop_error


class TestSWATOperationsImplConcatAble:
    """Test ConcatAble protocol implementation."""

    def test_concat_tables_success(self):
        """Should concatenate tables and return result table."""
        # Arrange
        operation = Mock()
        operation.call_action = Mock(return_value=Ok({"status": "OK"}))
        operation._session = Mock()
        result_table = Mock()
        operation._session.CASTable = Mock(return_value=result_table)

        ops = SWATOperationsImpl(operation)
        input_tables = [Mock(), Mock()]

        # Act
        result = ops.concat_tables(
            inputs=input_tables,
            caslib="mycaslib",
            output_table="concatenated",
            replace=True,
        )

        # Assert
        assert result.is_ok
        assert result.value is result_table
        operation.call_action.assert_called_once_with(
            "table.concat",
            casout={"name": "concatenated", "caslib": "mycaslib", "replace": True},
            inputs=input_tables,
        )
        operation._session.CASTable.assert_called_once_with(
            name="concatenated",
            caslib="mycaslib",
        )

    def test_concat_tables_error(self):
        """Should return error when concat action fails."""
        # Arrange
        operation = Mock()
        concat_error = OperationError(
            code=OperationErrorCode.SWAT_EXECUTION_ERROR,
            message="Concat failed",
        )
        operation.call_action = Mock(return_value=Err(concat_error))

        ops = SWATOperationsImpl(operation)

        # Act
        result = ops.concat_tables(
            inputs=[Mock()],
            caslib="mycaslib",
            output_table="output",
        )

        # Assert
        assert result.is_err
        assert result.error is concat_error


class TestSWATOperationsImplValidateAble:
    """Test ValidateAble protocol implementation."""

    def test_ensure_exists_table_exists(self):
        """Should return same table object when table exists."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        library_table = Mock()
        library_table.exists = Mock(return_value=True)
        library_table.params = {"name": "mytable", "caslib": "mycaslib"}

        # Act
        result = ops.ensure_exists(library_table)

        # Assert
        assert result.is_ok
        assert result.value is library_table  # Zero conversion cost
        library_table.exists.assert_called_once()

    def test_ensure_exists_table_not_found(self):
        """Should return TableNotFoundError when table doesn't exist."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        library_table = Mock()
        library_table.exists = Mock(return_value=False)
        library_table.params = {"name": "missing_table", "caslib": "mycaslib"}

        # Act
        result = ops.ensure_exists(library_table)

        # Assert
        assert result.is_err
        assert isinstance(result.error, TableNotFoundError)
        assert result.error.code == OperationErrorCode.TABLE_NOT_FOUND
        assert "missing_table" in result.error.message
        assert "mycaslib" in result.error.message

    def test_ensure_exists_exception_during_check(self):
        """Should return TableNotFoundError when exists() throws exception."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        library_table = Mock()
        check_error = RuntimeError("Connection lost")
        library_table.exists = Mock(side_effect=check_error)

        # Act
        result = ops.ensure_exists(library_table)

        # Assert
        assert result.is_err
        assert isinstance(result.error, TableNotFoundError)
        assert "Failed to check table existence" in result.error.message
        assert result.error.__cause__ is check_error


class TestSWATOperationsImplActionExecutable:
    """Test ActionExecutable protocol implementation."""

    def test_execute_action_success(self):
        """Should execute action and return result."""
        # Arrange
        operation = Mock()
        action_result = {"data": [1, 2, 3], "status": "OK"}
        operation.call_action = Mock(return_value=Ok(action_result))
        ops = SWATOperationsImpl(operation)

        # Act
        result = ops.execute_action(
            "astore.score",
            rstore="mymodel",
            table="mytable",
        )

        # Assert
        assert result.is_ok
        assert result.value == action_result
        operation.call_action.assert_called_once_with(
            "astore.score",
            rstore="mymodel",
            table="mytable",
        )

    def test_execute_action_error(self):
        """Should return error when action execution fails."""
        # Arrange
        operation = Mock()
        action_error = OperationError(
            code=OperationErrorCode.ACTION_NOT_FOUND,
            message="Action not found",
        )
        operation.call_action = Mock(return_value=Err(action_error))
        ops = SWATOperationsImpl(operation)

        # Act
        result = ops.execute_action("invalid.action")

        # Assert
        assert result.is_err
        assert result.error is action_error


class TestSWATOperationsImplResultParseable:
    """Test ResultParseable protocol implementation."""

    def test_extract_astore_payload_with_output_tables(self):
        """Should extract OutputCasTables from astore result."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        output_tables_mock = Mock()
        output_tables_mock.to_dict = Mock(
            return_value=[
                {"caslib": "mycaslib", "name": "scored_table", "rows": 100},
            ]
        )
        result_data = MagicMock()
        result_data.get = Mock(return_value=output_tables_mock)

        # Act
        result = ops.extract_astore_payload(result_data)

        # Assert
        assert result.is_ok
        payload = result.value
        assert "output_tables" in payload
        assert len(payload["output_tables"]) == 1
        assert payload["output_tables"][0]["name"] == "scored_table"

    def test_extract_astore_payload_empty(self):
        """Should return empty dict when no payload found."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        result_data = MagicMock()
        result_data.get = Mock(return_value=None)

        # Act
        result = ops.extract_astore_payload(result_data)

        # Assert
        assert result.is_ok
        assert result.value == {}

    def test_extract_astore_payload_error(self):
        """Should return error when parsing fails."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        result_data = Mock()
        result_data.get = Mock(side_effect=AttributeError("Invalid result"))

        # Act
        result = ops.extract_astore_payload(result_data)

        # Assert
        assert result.is_err
        assert isinstance(result.error, OperationError)
        assert result.error.code == OperationErrorCode.PARSE_FAILED

    def test_extract_shapley_values_success(self):
        """Should extract Shapley values from result."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        shapley_mock = Mock()
        shapley_mock.to_dict = Mock(
            return_value=[
                {"Variable": "age", "Value": 0.5},
                {"Variable": "income", "Value": 0.3},
            ]
        )
        result_data = MagicMock()
        result_data.get = Mock(return_value=shapley_mock)

        # Act
        result = ops.extract_shapley_values(result_data)

        # Assert
        assert result.is_ok
        shapley_values = result.value
        assert len(shapley_values) == 2
        assert shapley_values[0]["Variable"] == "age"
        assert shapley_values[1]["Variable"] == "income"

    def test_extract_shapley_values_empty(self):
        """Should return empty list when no Shapley values found."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        result_data = MagicMock()
        result_data.get = Mock(return_value=None)

        # Act
        result = ops.extract_shapley_values(result_data)

        # Assert
        assert result.is_ok
        assert result.value == []

    def test_extract_shapley_values_error(self):
        """Should return error when parsing fails."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        result_data = Mock()
        result_data.get = Mock(side_effect=RuntimeError("Parse error"))

        # Act
        result = ops.extract_shapley_values(result_data)

        # Assert
        assert result.is_err
        assert isinstance(result.error, OperationError)
        assert result.error.code == OperationErrorCode.PARSE_FAILED

    def test_extract_status_with_boolean_status(self):
        """Should extract boolean status and message."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        result_data = MagicMock()
        result_data.get = Mock(
            side_effect=lambda key: {
                "status": True,
                "message": "Operation successful",
            }.get(key)
        )

        # Act
        result = ops.extract_status(result_data)

        # Assert
        assert result.is_ok
        success, message = result.value
        assert success is True
        assert message == "Operation successful"

    def test_extract_status_default_ok(self):
        """Should default to (True, 'OK') when no status found."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        result_data = MagicMock()
        result_data.get = Mock(return_value=None)

        # Act
        result = ops.extract_status(result_data)

        # Assert
        assert result.is_ok
        success, message = result.value
        assert success is True
        assert message == "OK"

    def test_extract_status_error(self):
        """Should return error when parsing fails."""
        # Arrange
        operation = Mock()
        ops = SWATOperationsImpl(operation)
        result_data = Mock()
        result_data.get = Mock(side_effect=Exception("Parse error"))

        # Act
        result = ops.extract_status(result_data)

        # Assert
        assert result.is_err
        assert isinstance(result.error, OperationError)
        assert result.error.code == OperationErrorCode.PARSE_FAILED


class TestSWATOperationsImplInitialization:
    """Test SWATOperationsImpl initialization."""

    def test_initialization(self):
        """Should initialize with OperationProtocol."""
        # Arrange
        operation = Mock()

        # Act
        ops = SWATOperationsImpl(operation)

        # Assert
        assert ops.operation is operation
