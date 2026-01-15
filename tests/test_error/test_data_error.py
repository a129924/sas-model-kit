"""Tests for data-level error types."""

import pickle

from sas_model_kit.error import (
    ColumnNotFoundError,
    DataError,
    DataErrorCode,
    DataTypeMismatchError,
    InvalidDataError,
    SchemaMismatchError,
)


class TestDataErrorCode:
    def test_enum_values(self):
        assert DataErrorCode.COLUMN_NOT_FOUND.value == "COLUMN_NOT_FOUND"
        assert DataErrorCode.SCHEMA_MISMATCH.value == "SCHEMA_MISMATCH"
        assert DataErrorCode.DATA_TYPE_MISMATCH.value == "DATA_TYPE_MISMATCH"
        assert DataErrorCode.INVALID_DATA.value == "INVALID_DATA"


class TestDataError:
    def test_basic_initialization(self):
        err = DataError(DataErrorCode.INVALID_DATA, "bad data")
        assert err.code == DataErrorCode.INVALID_DATA
        assert err.message == "bad data"
        assert err.cause is None
        assert err.args == (DataErrorCode.INVALID_DATA.value, "bad data")

    def test_cause_sets_exception_chain(self):
        cause = RuntimeError("boom")
        err = DataError(DataErrorCode.UNKNOWN, "failed", cause=cause)
        assert err.cause is cause
        assert err.__cause__ is cause

    def test_pickle_roundtrip(self):
        err = DataError(DataErrorCode.INVALID_DATA, "bad data")
        restored = pickle.loads(pickle.dumps(err))
        assert restored.code == DataErrorCode.INVALID_DATA
        assert restored.message == "bad data"


class TestNamedDataErrors:
    def test_column_not_found_error(self):
        err = ColumnNotFoundError("missing column")
        assert err.code == DataErrorCode.COLUMN_NOT_FOUND

    def test_schema_mismatch_error(self):
        err = SchemaMismatchError("schema mismatch")
        assert err.code == DataErrorCode.SCHEMA_MISMATCH

    def test_data_type_mismatch_error(self):
        err = DataTypeMismatchError("type mismatch")
        assert err.code == DataErrorCode.DATA_TYPE_MISMATCH

    def test_invalid_data_error(self):
        err = InvalidDataError("invalid")
        assert err.code == DataErrorCode.INVALID_DATA
