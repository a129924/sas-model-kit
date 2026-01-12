"""Tests for concrete error classes."""

from sas_model_kit.error import (
    BaseError,
    ConflictingRuleFailure,
    DataFetchFailure,
    DuplicateKeyError,
    InvalidColumnFailure,
    InvalidTypeFailure,
    MissingFieldFailure,
    OperationError,
    SortError,
    TransformationFailure,
    UploadFailure,
    ValidationFailure,
)


def test_operation_error_inherits_base() -> None:
    err = OperationError(code="OP001", message="operation failed")
    assert isinstance(err, BaseError)


def test_datasource_errors_inherit_base() -> None:
    upload_err = UploadFailure(code="UP001", message="upload failed")
    fetch_err = DataFetchFailure(code="DF001", message="fetch failed")
    assert isinstance(upload_err, BaseError)
    assert isinstance(fetch_err, BaseError)


def test_transformation_errors_defaults() -> None:
    base = TransformationFailure(code="TR000", message="transform")
    invalid = InvalidColumnFailure(
        code="TR001",
        message="missing cols",
        columns=["a"],
        available_columns=["b", "c"],
    )
    sort_err = SortError(code="TR002", message="sort", reason="bad order")
    dup_err = DuplicateKeyError(
        code="TR003",
        message="dup",
        key_column="id",
        duplicate_count=2,
    )
    assert isinstance(base, BaseError)
    assert base.operation == ""
    assert invalid.columns == ["a"]
    assert invalid.available_columns == ["b", "c"]
    assert sort_err.reason == "bad order"
    assert dup_err.key_column == "id"
    assert dup_err.duplicate_count == 2


def test_parameter_errors_defaults() -> None:
    base = ValidationFailure(code="P000", message="base", field_name="x")
    missing = MissingFieldFailure(code="P001", message="missing", field_name="y")
    invalid = InvalidTypeFailure(
        code="P002",
        message="type",
        expected_type="int",
        actual_type="str",
    )
    conflict = ConflictingRuleFailure(
        code="P003",
        message="conflict",
        conflicting_fields=["a", "b"],
    )
    assert isinstance(base, BaseError)
    assert missing.field_name == "y"
    assert invalid.expected_type == "int"
    assert invalid.actual_type == "str"
    assert conflict.conflicting_fields == ["a", "b"]
