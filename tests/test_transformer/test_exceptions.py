"""Tests for Transformer exceptions."""

import pytest

from sas_model_kit.transformer.exceptions import (
    ColumnConflictError,
    InvalidColumnError,
    TableNotFoundError,
    TransformationError,
)


def test_transformation_error_inheritance() -> None:
    """Test TransformationError is a subclass of Exception."""
    assert issubclass(TransformationError, Exception)


def test_invalid_column_error_inheritance() -> None:
    """Test InvalidColumnError inherits from TransformationError."""
    assert issubclass(InvalidColumnError, TransformationError)
    assert issubclass(InvalidColumnError, Exception)


def test_table_not_found_error_inheritance() -> None:
    """Test TableNotFoundError inherits from TransformationError."""
    assert issubclass(TableNotFoundError, TransformationError)
    assert issubclass(TableNotFoundError, Exception)


def test_column_conflict_error_inheritance() -> None:
    """Test ColumnConflictError inherits from TransformationError."""
    assert issubclass(ColumnConflictError, TransformationError)
    assert issubclass(ColumnConflictError, Exception)


def test_transformation_error_message() -> None:
    """Test TransformationError can hold a message."""
    error = TransformationError("test message")
    assert str(error) == "test message"


def test_invalid_column_error_message() -> None:
    """Test InvalidColumnError can hold a message."""
    error = InvalidColumnError("Column 'age' not found")
    assert str(error) == "Column 'age' not found"


def test_table_not_found_error_message() -> None:
    """Test TableNotFoundError can hold a message."""
    error = TableNotFoundError("Table public.missing not found")
    assert str(error) == "Table public.missing not found"


def test_column_conflict_error_message() -> None:
    """Test ColumnConflictError can hold a message."""
    error = ColumnConflictError("Column '_id' already exists")
    assert str(error) == "Column '_id' already exists"


def test_catch_specific_error() -> None:
    """Test catching specific error types."""
    with pytest.raises(InvalidColumnError):
        raise InvalidColumnError("test")


def test_catch_transformation_error_base() -> None:
    """Test catching TransformationError catches all subclasses."""
    with pytest.raises(TransformationError):
        raise InvalidColumnError("test")

    with pytest.raises(TransformationError):
        raise TableNotFoundError("test")

    with pytest.raises(TransformationError):
        raise ColumnConflictError("test")


def test_raise_and_catch_transformation_error() -> None:
    """Test raising and catching TransformationError."""
    try:
        raise TransformationError("operation failed")
    except TransformationError as e:
        assert str(e) == "operation failed"
    else:
        pytest.fail("Should have raised TransformationError")


def test_raise_with_cause() -> None:
    """Test raising with original exception as cause."""
    original = ValueError("original error")

    try:
        try:
            raise original
        except ValueError as e:
            raise TransformationError("transformation failed") from e
    except TransformationError as e:
        assert e.__cause__ == original
        assert isinstance(e.__cause__, ValueError)
