"""Tests for AddUniqueKeyTransformer."""

from unittest.mock import Mock

import pytest

from sas_model_kit.error import DuplicateKeyError, OperationError, OperationErrorCode
from sas_model_kit.result import Err, Ok
from sas_model_kit.transformer.unique_key import AddUniqueKeyTransformer


@pytest.fixture
def mock_operation():
    """Mock operation for testing."""
    return Mock()


@pytest.fixture
def mock_table():
    """Mock CASTable for testing."""
    table = Mock()
    table.columns = ["id", "name", "age", "salary"]
    table.params = {"name": "test_table", "caslib": "public"}
    table.get_connection = Mock(return_value=Mock())
    return table


def test_unique_key_default_name(mock_operation, mock_table) -> None:
    """Test adding unique key with default column name."""
    transformer = AddUniqueKeyTransformer(mock_operation)
    mock_operation.call_action.return_value = Ok(Mock(status=None))

    result = transformer.execute(mock_table)

    # Verify DATA step was called
    mock_operation.call_action.assert_called_once()
    call_args = mock_operation.call_action.call_args
    assert call_args[0][0] == "datastep.runcode"
    code = call_args[1]["code"]
    assert "_id = _threadid_ * 1000000000 + _N_;" in code
    assert result.is_ok
    assert result.value is mock_table.get_connection.return_value.CASTable.return_value


def test_unique_key_custom_name(mock_operation, mock_table) -> None:
    """Test adding unique key with custom column name."""
    transformer = AddUniqueKeyTransformer(mock_operation, column_name="row_id")
    mock_operation.call_action.return_value = Ok(Mock(status=None))

    result = transformer.execute(mock_table)

    code = mock_operation.call_action.call_args[1]["code"]
    assert "row_id = _threadid_ * 1000000000 + _N_;" in code
    assert result.is_ok
    assert result.value is mock_table.get_connection.return_value.CASTable.return_value


def test_unique_key_column_conflict_raises(mock_operation, mock_table) -> None:
    """Test that existing column name raises error."""
    mock_table.columns = ["_id", "name", "age"]
    transformer = AddUniqueKeyTransformer(mock_operation)

    result = transformer.execute(mock_table)

    assert result.is_err
    assert isinstance(result.error, DuplicateKeyError)


def test_unique_key_invalid_column_name_raises(mock_operation) -> None:
    """Test that invalid column name raises error."""
    with pytest.raises(ValueError, match="Invalid column_name"):
        AddUniqueKeyTransformer(mock_operation, column_name="abc-def")


def test_unique_key_custom_output_table(mock_operation, mock_table) -> None:
    """Test custom output table name."""
    transformer = AddUniqueKeyTransformer(mock_operation, output_table="my_result")
    mock_operation.call_action.return_value = Ok(Mock(status=None))

    result = transformer.execute(mock_table)

    code = mock_operation.call_action.call_args[1]["code"]
    assert "data public.my_result;" in code
    assert result.is_ok
    assert result.value is mock_table.get_connection.return_value.CASTable.return_value


def test_unique_key_custom_output_caslib(mock_operation, mock_table) -> None:
    """Test custom output CAS library."""
    transformer = AddUniqueKeyTransformer(mock_operation, output_caslib="mylib")
    mock_operation.call_action.return_value = Ok(Mock(status=None))

    result = transformer.execute(mock_table)

    code = mock_operation.call_action.call_args[1]["code"]
    assert "data mylib." in code
    assert result.is_ok
    assert result.value is mock_table.get_connection.return_value.CASTable.return_value


def test_unique_key_execution_failure_raises(mock_operation, mock_table) -> None:
    """Test that operation failure raises TransformationError."""
    transformer = AddUniqueKeyTransformer(mock_operation)
    mock_operation.call_action.return_value = Err(
        OperationError(code=OperationErrorCode.UNKNOWN, message="CAS error")
    )

    result = transformer.execute(mock_table)

    assert result.is_err
    assert isinstance(result.error, OperationError)


def test_unique_key_bad_status_raises(mock_operation, mock_table) -> None:
    """Test that bad DATA step status raises error."""
    transformer = AddUniqueKeyTransformer(mock_operation)
    mock_operation.call_action.return_value = Ok(Mock(status="ERROR"))

    result = transformer.execute(mock_table)

    assert result.is_err
    assert isinstance(result.error, OperationError)


def test_unique_key_stores_operation(mock_operation, mock_table) -> None:
    """Test that transformer stores operation."""
    transformer = AddUniqueKeyTransformer(mock_operation)
    assert transformer.operation is mock_operation


def test_unique_key_stores_parameters(mock_operation) -> None:
    """Test that transformer stores parameters."""
    transformer = AddUniqueKeyTransformer(
        mock_operation, column_name="pk", output_caslib="lib2", output_table="tbl2"
    )

    assert transformer.column_name == "pk"
    assert transformer.output_caslib == "lib2"
    assert transformer.output_table == "tbl2"


def test_unique_key_returns_new_table(mock_operation, mock_table) -> None:
    """Test that execute returns a new table instance."""
    transformer = AddUniqueKeyTransformer(mock_operation)
    mock_operation.call_action.return_value = Ok(Mock(status=None))

    result = transformer.execute(mock_table)

    # Verify connection.CASTable was called
    mock_connection = mock_table.get_connection.return_value
    mock_connection.CASTable.assert_called_once()
    assert result.is_ok
    assert result.value is mock_connection.CASTable.return_value


def test_unique_key_with_default_output_name(mock_operation, mock_table) -> None:
    """Test auto-generated output table name."""
    transformer = AddUniqueKeyTransformer(mock_operation)
    mock_operation.call_action.return_value = Ok(Mock(status=None))

    result = transformer.execute(mock_table)

    code = mock_operation.call_action.call_args[1]["code"]
    # Should contain test_table_with__id_<timestamp>
    assert "test_table_with__id_" in code
    assert result.is_ok
    assert result.value is mock_table.get_connection.return_value.CASTable.return_value


def test_unique_key_preserves_input_columns(mock_operation, mock_table) -> None:
    """Test that DATA step preserves all input columns."""
    transformer = AddUniqueKeyTransformer(mock_operation)
    mock_operation.call_action.return_value = Ok(Mock(status=None))

    result = transformer.execute(mock_table)

    code = mock_operation.call_action.call_args[1]["code"]
    # Should have SET statement that reads all input columns
    assert "set public.test_table;" in code
    assert result.is_ok
    assert result.value is mock_table.get_connection.return_value.CASTable.return_value
