"""Tests for Phase 5 OperationError (Exception-based).

This test module validates the new OperationError design that:
- Inherits from Exception (not BaseError)
- Uses OperationErrorCode Enum for type safety
- Supports pickle serialization
- Auto-sets __cause__ for error chaining
"""

from __future__ import annotations

import pickle

import pytest

from sas_model_kit.error import (
    OperationError,
    OperationErrorCode,
    TableNotFoundError,
)


class TestOperationErrorCode:
    """Test OperationErrorCode Enum."""

    def test_enum_values(self) -> None:
        """All expected error codes exist."""
        assert OperationErrorCode.ACTION_SET_NOT_FOUND.value == "ACTION_SET_NOT_FOUND"
        assert OperationErrorCode.ACTION_NOT_FOUND.value == "ACTION_NOT_FOUND"
        assert OperationErrorCode.SWAT_EXECUTION_ERROR.value == "SWAT_EXECUTION_ERROR"
        assert OperationErrorCode.TABLE_NOT_FOUND.value == "TABLE_NOT_FOUND"
        assert OperationErrorCode.READ_FAILED.value == "READ_FAILED"
        assert OperationErrorCode.WRITE_FAILED.value == "WRITE_FAILED"
        assert OperationErrorCode.SORT_FAILED.value == "SORT_FAILED"
        assert OperationErrorCode.PARSE_FAILED.value == "PARSE_FAILED"
        assert OperationErrorCode.UNKNOWN.value == "UNKNOWN"

    def test_enum_count(self) -> None:
        """Exactly 9 error codes defined."""
        assert len(OperationErrorCode) == 9

    def test_enum_type_safety(self) -> None:
        """Enum provides type safety."""
        code: OperationErrorCode = OperationErrorCode.READ_FAILED
        assert isinstance(code, OperationErrorCode)


class TestOperationError:
    """Test OperationError Exception."""

    def test_basic_creation(self) -> None:
        """Can create OperationError with code and message."""
        err = OperationError(
            code=OperationErrorCode.READ_FAILED, message="Failed to read table"
        )
        assert err.code == OperationErrorCode.READ_FAILED
        assert err.message == "Failed to read table"
        assert err.cause is None

    def test_inherits_exception(self) -> None:
        """OperationError properly inherits Exception."""
        err = OperationError(code=OperationErrorCode.READ_FAILED, message="test")
        assert isinstance(err, Exception)

    def test_exception_args_set(self) -> None:
        """Exception.args are properly set."""
        err = OperationError(
            code=OperationErrorCode.READ_FAILED, message="test message"
        )
        # Should have (code.value, message) in args
        assert len(err.args) == 2
        assert err.args[0] == "READ_FAILED"
        assert err.args[1] == "test message"

    def test_with_cause(self) -> None:
        """Can set cause parameter."""
        original_error = ValueError("Original error")
        err = OperationError(
            code=OperationErrorCode.SWAT_EXECUTION_ERROR,
            message="SWAT failed",
            cause=original_error,
        )
        assert err.cause is original_error
        # Auto-set __cause__
        assert err.__cause__ is original_error

    def test_auto_cause_chaining(self) -> None:
        """__cause__ is automatically set for error chaining."""
        original = RuntimeError("Original")
        err = OperationError(
            code=OperationErrorCode.SWAT_EXECUTION_ERROR,
            message="Wrapped",
            cause=original,
        )
        # Both should be set
        assert err.cause is original
        assert err.__cause__ is original

    def test_no_cause_when_none(self) -> None:
        """__cause__ not set when cause is None."""
        err = OperationError(code=OperationErrorCode.READ_FAILED, message="test")
        assert err.cause is None
        # __cause__ should remain None (not explicitly set)
        assert err.__cause__ is None

    def test_str_representation(self) -> None:
        """__str__ shows code and message."""
        err = OperationError(
            code=OperationErrorCode.WRITE_FAILED, message="Cannot write to table"
        )
        assert str(err) == "[WRITE_FAILED] Cannot write to table"

    def test_repr_representation(self) -> None:
        """__repr__ shows detailed info."""
        err = OperationError(code=OperationErrorCode.SORT_FAILED, message="Sort failed")
        repr_str = repr(err)
        assert "OperationError" in repr_str
        assert "SORT_FAILED" in repr_str
        assert "Sort failed" in repr_str

    def test_repr_with_cause(self) -> None:
        """__repr__ includes cause when present."""
        original = ValueError("test")
        err = OperationError(
            code=OperationErrorCode.READ_FAILED, message="read failed", cause=original
        )
        repr_str = repr(err)
        assert "cause=" in repr_str

    def test_pickle_serialization(self) -> None:
        """OperationError can be pickled and unpickled."""
        err = OperationError(code=OperationErrorCode.READ_FAILED, message="pickle test")
        # Pickle and unpickle
        pickled = pickle.dumps(err)
        restored = pickle.loads(pickled)

        assert restored.code == OperationErrorCode.READ_FAILED
        assert restored.message == "pickle test"
        assert restored.cause is None

    def test_pickle_with_cause(self) -> None:
        """OperationError with cause can be pickled."""
        original = ValueError("original")
        err = OperationError(
            code=OperationErrorCode.SWAT_EXECUTION_ERROR,
            message="with cause",
            cause=original,
        )
        # Pickle and unpickle
        pickled = pickle.dumps(err)
        restored = pickle.loads(pickled)

        assert restored.code == OperationErrorCode.SWAT_EXECUTION_ERROR
        assert restored.message == "with cause"
        # cause should be restored
        assert restored.cause is not None
        assert isinstance(restored.cause, ValueError)
        assert str(restored.cause) == "original"

    def test_can_raise_and_catch(self) -> None:
        """OperationError can be raised and caught."""
        with pytest.raises(OperationError) as exc_info:
            raise OperationError(
                code=OperationErrorCode.ACTION_SET_NOT_FOUND,
                message="actionset not loaded",
            )
        assert exc_info.value.code == OperationErrorCode.ACTION_SET_NOT_FOUND

    def test_match_case_pattern(self) -> None:
        """OperationError supports match/case with Enum code."""
        err = OperationError(
            code=OperationErrorCode.ACTION_SET_NOT_FOUND, message="test"
        )

        # Python 3.10+ match/case
        matched = False
        match err.code:
            case OperationErrorCode.ACTION_SET_NOT_FOUND:
                matched = True
            case _:
                matched = False

        assert matched is True


class TestTableNotFoundError:
    """Test TableNotFoundError (named error)."""

    def test_inherits_operation_error(self) -> None:
        """TableNotFoundError inherits OperationError."""
        err = TableNotFoundError(message="Table not found")
        assert isinstance(err, OperationError)
        assert isinstance(err, Exception)

    def test_auto_sets_code(self) -> None:
        """TableNotFoundError auto-sets TABLE_NOT_FOUND code."""
        err = TableNotFoundError(message="missing table")
        assert err.code == OperationErrorCode.TABLE_NOT_FOUND

    def test_with_message(self) -> None:
        """Can create with custom message."""
        err = TableNotFoundError(message="Table public.data not found")
        assert err.message == "Table public.data not found"

    def test_with_cause(self) -> None:
        """Can pass cause to TableNotFoundError."""
        original = RuntimeError("SWAT error")
        err = TableNotFoundError(message="Table missing", cause=original)
        assert err.cause is original
        assert err.__cause__ is original

    def test_isinstance_check(self) -> None:
        """Can use isinstance to check for TableNotFoundError."""
        err = TableNotFoundError(message="test")
        assert isinstance(err, TableNotFoundError)
        assert isinstance(err, OperationError)

    def test_can_raise_and_catch_specifically(self) -> None:
        """Can catch TableNotFoundError specifically."""
        with pytest.raises(TableNotFoundError) as exc_info:
            raise TableNotFoundError(message="table missing")
        assert exc_info.value.message == "table missing"

    def test_can_catch_as_operation_error(self) -> None:
        """TableNotFoundError can be caught as OperationError."""
        with pytest.raises(OperationError) as exc_info:
            raise TableNotFoundError(message="test")
        # Should catch as OperationError
        assert exc_info.value.code == OperationErrorCode.TABLE_NOT_FOUND

    def test_pickle_serialization(self) -> None:
        """TableNotFoundError can be pickled."""
        err = TableNotFoundError(message="pickle test")
        pickled = pickle.dumps(err)
        restored = pickle.loads(pickled)

        assert isinstance(restored, TableNotFoundError)
        assert restored.code == OperationErrorCode.TABLE_NOT_FOUND
        assert restored.message == "pickle test"


class TestErrorChaining:
    """Test error chaining behavior with __cause__."""

    def test_manual_error_chain(self) -> None:
        """Error chain preserved in exception handling."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise OperationError(
                    code=OperationErrorCode.READ_FAILED,
                    message="Failed to read",
                    cause=e,
                ) from e
        except OperationError as op_err:
            # Should have both cause and __cause__ set
            assert op_err.cause is not None
            assert op_err.__cause__ is not None
            assert isinstance(op_err.__cause__, ValueError)

    def test_auto_cause_without_from(self) -> None:
        """Auto __cause__ setting works without 'from' clause."""
        original = RuntimeError("test")
        err = OperationError(
            code=OperationErrorCode.SWAT_EXECUTION_ERROR,
            message="wrapped",
            cause=original,
        )
        # Both should be set even without 'from' clause
        assert err.cause is original
        assert err.__cause__ is original
