"""Tests for SWAT helper classes implementing Able Protocols."""

from unittest.mock import MagicMock, Mock, PropertyMock

import pytest

from sas_model_kit.error import (
    OperationError,
    OperationErrorCode,
    TableNotFoundError,
)
from sas_model_kit.helpers.swat.action_processor import SWATActionProcessor
from sas_model_kit.helpers.swat.table_lifecycle import SWATTableLifecycle
from sas_model_kit.helpers.swat.table_metadata import SWATTableMetadata
from sas_model_kit.helpers.swat.table_transform import SWATTableTransform
from sas_model_kit.result import Err, Ok


class TestSWATTableMetadataReadAble:
    """Test ReadAble implementation."""

    def test_get_columns_success(self):
        operation = Mock()
        ops = SWATTableMetadata(operation)
        table = Mock()
        table.columns = ["col1", "col2", "col3"]

        result = ops.get_columns(table)

        assert result.is_ok
        assert result.value == ["col1", "col2", "col3"]

    def test_get_columns_error(self):
        operation = Mock()
        ops = SWATTableMetadata(operation)
        table = Mock()
        original_error = ValueError("Invalid table")
        type(table).columns = PropertyMock(side_effect=original_error)

        result = ops.get_columns(table)

        assert result.is_err
        assert isinstance(result.error, OperationError)
        assert result.error.code == OperationErrorCode.READ_FAILED
        assert "Failed to get columns" in result.error.message
        assert result.error.__cause__ is original_error

    def test_get_table_location_success(self):
        operation = Mock()
        ops = SWATTableMetadata(operation)
        table = Mock()
        table.params = {"caslib": "mycaslib", "name": "mytable"}

        result = ops.get_table_location(table)

        assert result.is_ok
        assert result.value == ("mycaslib", "mytable")

    def test_get_table_location_default_caslib(self):
        operation = Mock()
        ops = SWATTableMetadata(operation)
        table = Mock()
        table.params = {"name": "mytable"}

        result = ops.get_table_location(table)

        assert result.is_ok
        assert result.value == ("public", "mytable")

    def test_get_table_location_missing_name_error(self):
        operation = Mock()
        ops = SWATTableMetadata(operation)
        table = Mock()
        table.params = {"caslib": "mycaslib"}

        result = ops.get_table_location(table)

        assert result.is_err
        assert isinstance(result.error, OperationError)
        assert result.error.code == OperationErrorCode.READ_FAILED


class TestSWATTableMetadataValidateAble:
    """Test ValidateAble implementation."""

    def test_ensure_exists_table_exists(self):
        operation = Mock()
        ops = SWATTableMetadata(operation)
        library_table = Mock()
        library_table.exists = Mock(return_value=True)
        library_table.params = {"name": "mytable", "caslib": "mycaslib"}

        result = ops.ensure_exists(library_table)

        assert result.is_ok
        assert result.value is library_table
        library_table.exists.assert_called_once()

    def test_ensure_exists_table_not_found(self):
        operation = Mock()
        ops = SWATTableMetadata(operation)
        library_table = Mock()
        library_table.exists = Mock(return_value=False)
        library_table.params = {"name": "missing_table", "caslib": "mycaslib"}

        result = ops.ensure_exists(library_table)

        assert result.is_err
        assert isinstance(result.error, TableNotFoundError)
        assert result.error.code == OperationErrorCode.TABLE_NOT_FOUND
        assert "missing_table" in result.error.message
        assert "mycaslib" in result.error.message

    def test_ensure_exists_exception_during_check(self):
        operation = Mock()
        ops = SWATTableMetadata(operation)
        library_table = Mock()
        check_error = RuntimeError("Connection lost")
        library_table.exists = Mock(side_effect=check_error)

        result = ops.ensure_exists(library_table)

        assert result.is_err
        assert isinstance(result.error, TableNotFoundError)
        assert "Failed to check table existence" in result.error.message
        assert result.error.__cause__ is check_error


class TestSWATTableLifecycleWriteAble:
    """Test WriteAble implementation."""

    def test_create_table_success(self):
        operation = Mock()
        operation.upload_data = Mock(return_value=Ok(None))
        operation._session = Mock()
        mock_table = Mock()
        operation._session.CASTable = Mock(return_value=mock_table)

        ops = SWATTableLifecycle(operation)
        source_data = Mock()

        result = ops.create_table(
            name="newtable",
            caslib="mycaslib",
            source=source_data,
            replace=True,
        )

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
        operation = Mock()
        upload_error = OperationError(
            code=OperationErrorCode.WRITE_FAILED,
            message="Upload failed",
        )
        operation.upload_data = Mock(return_value=Err(upload_error))

        ops = SWATTableLifecycle(operation)
        source_data = Mock()

        result = ops.create_table(
            name="newtable",
            caslib="mycaslib",
            source=source_data,
        )

        assert result.is_err
        assert isinstance(result.error, OperationError)
        assert result.error.code == OperationErrorCode.WRITE_FAILED
        assert "Failed to upload data for table 'newtable'" in result.error.message

    def test_create_table_exception(self):
        operation = Mock()
        operation.upload_data = Mock(side_effect=RuntimeError("Unexpected error"))

        ops = SWATTableLifecycle(operation)

        result = ops.create_table(
            name="newtable",
            caslib="mycaslib",
            source=Mock(),
        )

        assert result.is_err
        assert isinstance(result.error, OperationError)
        assert result.error.code == OperationErrorCode.WRITE_FAILED


class TestSWATTableLifecycleDeleteAble:
    """Test DeleteAble implementation."""

    def test_drop_table_success(self):
        operation = Mock()
        operation.call_action = Mock(return_value=Ok({"status": "OK"}))
        ops = SWATTableLifecycle(operation)

        result = ops.drop_table(caslib="mycaslib", table="mytable")

        assert result.is_ok
        assert result.value is None
        operation.call_action.assert_called_once_with(
            "table.dropTable",
            caslib="mycaslib",
            name="mytable",
        )

    def test_drop_table_error(self):
        operation = Mock()
        drop_error = OperationError(
            code=OperationErrorCode.SWAT_EXECUTION_ERROR,
            message="Table not found",
        )
        operation.call_action = Mock(return_value=Err(drop_error))
        ops = SWATTableLifecycle(operation)

        result = ops.drop_table(caslib="mycaslib", table="mytable")

        assert result.is_err
        assert result.error is drop_error


class TestSWATTableTransformSortAble:
    """Test SortAble implementation."""

    def test_sort_values_single_column_ascending(self):
        operation = Mock()
        ops = SWATTableTransform(operation)
        table = Mock()
        sorted_table = Mock()
        table.sort_values = Mock(return_value=sorted_table)

        result = ops.sort_values(table, by=["col1"], ascending=True)

        assert result.is_ok
        assert result.value is sorted_table
        table.sort_values.assert_called_once_with(by=["col1"], ascending=True)

    def test_sort_values_multiple_columns(self):
        operation = Mock()
        ops = SWATTableTransform(operation)
        table = Mock()
        sorted_table = Mock()
        table.sort_values = Mock(return_value=sorted_table)

        result = ops.sort_values(table, by=["col1", "col2"], ascending=[True, False])

        assert result.is_ok
        table.sort_values.assert_called_once_with(
            by=["col1", "col2"],
            ascending=[True, False],
        )

    def test_sort_values_error(self):
        operation = Mock()
        ops = SWATTableTransform(operation)
        table = Mock()
        sort_error = ValueError("Invalid column")
        table.sort_values = Mock(side_effect=sort_error)

        result = ops.sort_values(table, by=["invalid_col"])

        assert result.is_err
        assert isinstance(result.error, OperationError)
        assert result.error.code == OperationErrorCode.SORT_FAILED
        assert result.error.__cause__ is sort_error


class TestSWATTableTransformConcatAble:
    """Test ConcatAble implementation."""

    def test_concat_tables_success(self, monkeypatch):
        operation = Mock()
        ops = SWATTableTransform(operation)
        input_tables = [Mock(), Mock()]
        result_table = Mock()

        def fake_concat(inputs, caslib, name, replace):
            assert inputs == input_tables
            assert caslib == "mycaslib"
            assert name == "concatenated"
            assert replace is True
            return result_table

        monkeypatch.setattr("swat.functions.concat", fake_concat)

        result = ops.concat_tables(
            inputs=input_tables,
            caslib="mycaslib",
            output_table="concatenated",
            replace=True,
        )

        assert result.is_ok
        assert result.value is result_table

    def test_concat_tables_error(self, monkeypatch):
        operation = Mock()
        ops = SWATTableTransform(operation)

        from swat.exceptions import SWATError

        def fake_concat(*_args, **_kwargs):
            raise SWATError("Concat failed")

        monkeypatch.setattr("swat.functions.concat", fake_concat)

        result = ops.concat_tables(
            inputs=[Mock()],
            caslib="mycaslib",
            output_table="output",
        )

        assert result.is_err
        assert isinstance(result.error, OperationError)
        assert result.error.code == OperationErrorCode.WRITE_FAILED


class TestSWATActionProcessorActionExecutable:
    """Test ActionExecutable implementation."""

    def test_execute_action_success(self):
        operation = Mock()
        action_result = {"data": [1, 2, 3], "status": "OK"}
        operation.call_action = Mock(return_value=Ok(action_result))
        ops = SWATActionProcessor(operation)

        result = ops.execute_action(
            "astore.score",
            rstore="mymodel",
            table="mytable",
        )

        assert result.is_ok
        assert result.value == action_result
        operation.call_action.assert_called_once_with(
            "astore.score",
            rstore="mymodel",
            table="mytable",
        )

    def test_execute_action_error(self):
        operation = Mock()
        action_error = OperationError(
            code=OperationErrorCode.ACTION_NOT_FOUND,
            message="Action not found",
        )
        operation.call_action = Mock(return_value=Err(action_error))
        ops = SWATActionProcessor(operation)

        result = ops.execute_action("invalid.action")

        assert result.is_err
        assert result.error is action_error


class TestSWATActionProcessorResultParseable:
    """Test ResultParseable implementation."""

    def test_extract_astore_payload_with_output_tables(self):
        operation = Mock()
        ops = SWATActionProcessor(operation)
        output_tables_mock = Mock()
        output_tables_mock.to_dict = Mock(
            return_value=[
                {"caslib": "mycaslib", "name": "scored_table", "rows": 100},
            ]
        )
        result_data = MagicMock()
        result_data.get = Mock(return_value=output_tables_mock)

        result = ops.extract_astore_payload(result_data)

        assert result.is_ok
        payload = result.value
        assert "output_tables" in payload
        assert len(payload["output_tables"]) == 1
        assert payload["output_tables"][0]["name"] == "scored_table"

    def test_extract_astore_payload_empty(self):
        operation = Mock()
        ops = SWATActionProcessor(operation)
        result_data = MagicMock()
        result_data.get = Mock(return_value=None)

        result = ops.extract_astore_payload(result_data)

        assert result.is_ok
        assert result.value == {}

    def test_extract_astore_payload_error(self):
        operation = Mock()
        ops = SWATActionProcessor(operation)
        result_data = Mock()
        result_data.get = Mock(side_effect=AttributeError("Invalid result"))

        result = ops.extract_astore_payload(result_data)

        assert result.is_err
        assert isinstance(result.error, OperationError)
        assert result.error.code == OperationErrorCode.PARSE_FAILED

    def test_extract_shapley_values_success(self):
        operation = Mock()
        ops = SWATActionProcessor(operation)
        shapley_mock = Mock()
        shapley_mock.to_dict = Mock(
            return_value=[
                {"Variable": "age", "Value": 0.5},
                {"Variable": "income", "Value": 0.3},
            ]
        )
        result_data = MagicMock()
        result_data.get = Mock(return_value=shapley_mock)

        result = ops.extract_shapley_values(result_data)

        assert result.is_ok
        shapley_values = result.value
        assert len(shapley_values) == 2
        assert shapley_values[0]["Variable"] == "age"
        assert shapley_values[1]["Variable"] == "income"

    def test_extract_shapley_values_empty(self):
        operation = Mock()
        ops = SWATActionProcessor(operation)
        result_data = MagicMock()
        result_data.get = Mock(return_value=None)

        result = ops.extract_shapley_values(result_data)

        assert result.is_ok
        assert result.value == []

    def test_extract_shapley_values_error(self):
        operation = Mock()
        ops = SWATActionProcessor(operation)
        result_data = Mock()
        result_data.get = Mock(side_effect=RuntimeError("Parse error"))

        result = ops.extract_shapley_values(result_data)

        assert result.is_err
        assert isinstance(result.error, OperationError)
        assert result.error.code == OperationErrorCode.PARSE_FAILED

    def test_extract_status_with_boolean_status(self):
        operation = Mock()
        ops = SWATActionProcessor(operation)
        result_data = MagicMock()
        result_data.get = Mock(
            side_effect=lambda key: {
                "status": True,
                "message": "Operation successful",
            }.get(key)
        )

        result = ops.extract_status(result_data)

        assert result.is_ok
        success, message = result.value
        assert success is True
        assert message == "Operation successful"

    def test_extract_status_default_ok(self):
        operation = Mock()
        ops = SWATActionProcessor(operation)
        result_data = MagicMock()
        result_data.get = Mock(return_value=None)

        result = ops.extract_status(result_data)

        assert result.is_ok
        success, message = result.value
        assert success is True
        assert message == "OK"

    def test_extract_status_error(self):
        operation = Mock()
        ops = SWATActionProcessor(operation)
        result_data = Mock()
        result_data.get = Mock(side_effect=Exception("Parse error"))

        result = ops.extract_status(result_data)

        assert result.is_err
        assert isinstance(result.error, OperationError)
        assert result.error.code == OperationErrorCode.PARSE_FAILED


class TestSWATHelpersInitialization:
    """Test SWAT helper initialization."""

    def test_initialization(self):
        operation = Mock()

        assert SWATTableMetadata(operation).operation is operation
        assert SWATTableLifecycle(operation).operation is operation
        assert SWATTableTransform(operation).operation is operation
        assert SWATActionProcessor(operation).operation is operation
