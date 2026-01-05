"""Tests for new ModelResult pattern (Result[ModelSuccess, ModelError])."""

import pytest

from sas_model_kit.result.base import Err, Ok
from sas_model_kit.result.execution_metadata import ExecutionMetadata
from sas_model_kit.result.model_result_new import ModelResult
from sas_model_kit.result.model_types import ModelError, ModelSuccess


class TestModelResultSuccess:
    """Tests for ModelResult with Ok/ModelSuccess."""

    def test_success_creation(self) -> None:
        """Test creating successful ModelResult."""
        metadata = ExecutionMetadata(execution_time_ms=100.0, rows_affected=50)
        success = ModelSuccess(data="result", metadata=metadata)
        result: ModelResult[str] = Ok(success)

        assert result.is_ok
        assert not result.is_err

    def test_success_unwrap(self) -> None:
        """Test unwrapping successful ModelResult."""
        metadata = ExecutionMetadata(execution_time_ms=100.0, rows_affected=50)
        success = ModelSuccess(data="result", metadata=metadata)
        result: ModelResult[str] = Ok(success)

        unwrapped = result.unwrap()
        assert unwrapped.data == "result"
        assert unwrapped.metadata.execution_time_ms == 100.0

    def test_success_with_none_data(self) -> None:
        """Test success with None data (no output scenario)."""
        metadata = ExecutionMetadata(
            execution_time_ms=50.0,
            rows_affected=0,
            intended_output_caslib="models",
            intended_output_table="results",
        )
        success = ModelSuccess(data=None, metadata=metadata)
        result: ModelResult[None] = Ok(success)

        unwrapped = result.unwrap()
        assert unwrapped.data is None
        assert unwrapped.metadata.intended_output_caslib == "models"

    def test_success_unwrap_or_default(self) -> None:
        """Test unwrap_or with successful result."""
        metadata = ExecutionMetadata(execution_time_ms=100.0, rows_affected=0)
        success = ModelSuccess(data="actual", metadata=metadata)
        result: ModelResult[str] = Ok(success)

        value = result.unwrap_or(ModelSuccess(data="default", metadata=metadata))
        assert value.data == "actual"


class TestModelResultError:
    """Tests for ModelResult with Err/ModelError."""

    def test_error_creation(self) -> None:
        """Test creating error ModelResult."""
        metadata = ExecutionMetadata(execution_time_ms=10.0, rows_affected=0)
        error = ModelError(message="Operation failed", metadata=metadata)
        result: ModelResult[str] = Err(error)

        assert result.is_err
        assert not result.is_ok

    def test_error_unwrap_raises(self) -> None:
        """Test unwrapping error raises RuntimeError."""
        metadata = ExecutionMetadata(execution_time_ms=10.0, rows_affected=0)
        error = ModelError(message="Operation failed", metadata=metadata)
        result: ModelResult[str] = Err(error)

        with pytest.raises(RuntimeError):
            result.unwrap()

    def test_error_with_cause(self) -> None:
        """Test error with exception cause."""
        metadata = ExecutionMetadata(execution_time_ms=10.0, rows_affected=0)
        cause = ValueError("Invalid input")
        error = ModelError(message="Validation failed", metadata=metadata, cause=cause)
        result: ModelResult[str] = Err(error)

        unwrapped_err = result.error
        assert unwrapped_err.cause is cause
        assert isinstance(unwrapped_err.cause, ValueError)

    def test_error_unwrap_or_default(self) -> None:
        """Test unwrap_or with error result."""
        metadata = ExecutionMetadata(execution_time_ms=10.0, rows_affected=0)
        error = ModelError(message="Failed", metadata=metadata)
        result: ModelResult[str] = Err(error)

        default_success = ModelSuccess(data="default", metadata=metadata)
        value = result.unwrap_or(default_success)
        assert value.data == "default"


class TestModelResultPatternTransition:
    """Tests demonstrating transition from old to new pattern."""

    def test_success_transition(self) -> None:
        """Demonstrate old vs new success pattern."""
        metadata = ExecutionMetadata(execution_time_ms=100.0, rows_affected=100)

        # New pattern: Result[ModelSuccess, ModelError]
        success = ModelSuccess(data="table_result", metadata=metadata)
        new_result: ModelResult[str] = Ok(success)

        # Access data
        assert new_result.is_ok
        assert new_result.unwrap().data == "table_result"
        assert new_result.unwrap().metadata.execution_time_ms == 100.0

    def test_error_transition(self) -> None:
        """Demonstrate old vs new error pattern."""
        metadata = ExecutionMetadata(execution_time_ms=50.0, rows_affected=0)
        cause = RuntimeError("CAS error")

        # New pattern: Error with cause chain
        error = ModelError(message="Execution failed", metadata=metadata, cause=cause)
        new_result: ModelResult[str] = Err(error)

        # Access error information
        assert new_result.is_err
        assert new_result.error.message == "Execution failed"
        assert new_result.error.cause is cause

    def test_generic_type_flexibility(self) -> None:
        """Test ModelResult works with different data types."""
        metadata = ExecutionMetadata(execution_time_ms=100.0, rows_affected=0)

        # With int
        success_int: ModelResult[int] = Ok(ModelSuccess(data=42, metadata=metadata))
        assert success_int.unwrap().data == 42

        # With None (no output)
        success_none: ModelResult[None] = Ok(ModelSuccess(data=None, metadata=metadata))
        assert success_none.unwrap().data is None

        # With dict
        success_dict: ModelResult[dict] = Ok(
            ModelSuccess(data={"key": "value"}, metadata=metadata)
        )
        assert success_dict.unwrap().data == {"key": "value"}
