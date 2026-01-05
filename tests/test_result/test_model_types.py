"""Tests for ModelSuccess and ModelError types."""

from dataclasses import FrozenInstanceError

import pytest

from sas_model_kit.result.execution_metadata import ExecutionMetadata
from sas_model_kit.result.model_types import ModelError, ModelSuccess


class TestModelSuccess:
    """Tests for ModelSuccess class."""

    def test_creation_with_data(self) -> None:
        """Test creating ModelSuccess with data."""
        metadata = ExecutionMetadata(execution_time_ms=100.0, rows_affected=50)
        success = ModelSuccess(data="result_data", metadata=metadata)

        assert success.data == "result_data"
        assert success.metadata == metadata

    def test_creation_with_none_data(self) -> None:
        """Test creating ModelSuccess with None data."""
        metadata = ExecutionMetadata(execution_time_ms=50.0, rows_affected=0)
        success = ModelSuccess(data=None, metadata=metadata)

        assert success.data is None
        assert success.metadata == metadata

    def test_is_frozen(self) -> None:
        """Test that ModelSuccess is frozen (immutable)."""
        metadata = ExecutionMetadata(execution_time_ms=100.0, rows_affected=0)
        success = ModelSuccess(data="data", metadata=metadata)

        with pytest.raises(FrozenInstanceError):
            success.data = "new_data"  # type: ignore

    def test_with_generic_type(self) -> None:
        """Test ModelSuccess as generic type."""
        metadata = ExecutionMetadata(execution_time_ms=100.0, rows_affected=0)
        success = ModelSuccess[str](data="text", metadata=metadata)

        assert isinstance(success.data, str)
        assert success.data == "text"

    def test_equality(self) -> None:
        """Test ModelSuccess equality."""
        metadata1 = ExecutionMetadata(execution_time_ms=100.0, rows_affected=0)
        metadata2 = ExecutionMetadata(execution_time_ms=100.0, rows_affected=0)

        success1 = ModelSuccess(data="data", metadata=metadata1)
        success2 = ModelSuccess(data="data", metadata=metadata2)

        assert success1 == success2

    def test_with_intended_output(self) -> None:
        """Test ModelSuccess with intended output metadata."""
        metadata = ExecutionMetadata(
            execution_time_ms=100.0,
            rows_affected=0,
            intended_output_caslib="models",
            intended_output_table="results",
        )
        success = ModelSuccess(data=None, metadata=metadata)

        assert success.metadata.intended_output_caslib == "models"
        assert success.metadata.intended_output_table == "results"


class TestModelError:
    """Tests for ModelError class."""

    def test_creation_with_message(self) -> None:
        """Test creating ModelError with just message."""
        metadata = ExecutionMetadata(execution_time_ms=10.0, rows_affected=0)
        error = ModelError(message="Operation failed", metadata=metadata)

        assert error.message == "Operation failed"
        assert error.metadata == metadata
        assert error.cause is None

    def test_creation_with_cause(self) -> None:
        """Test creating ModelError with exception cause."""
        metadata = ExecutionMetadata(execution_time_ms=10.0, rows_affected=0)
        cause = ValueError("Invalid value")
        error = ModelError(message="Validation failed", metadata=metadata, cause=cause)

        assert error.message == "Validation failed"
        assert error.cause is cause
        assert isinstance(error.cause, ValueError)

    def test_is_frozen(self) -> None:
        """Test that ModelError is frozen (immutable)."""
        metadata = ExecutionMetadata(execution_time_ms=10.0, rows_affected=0)
        error = ModelError(message="Error", metadata=metadata)

        with pytest.raises(FrozenInstanceError):
            error.message = "New message"  # type: ignore

    def test_equality(self) -> None:
        """Test ModelError equality."""
        metadata1 = ExecutionMetadata(execution_time_ms=10.0, rows_affected=0)
        metadata2 = ExecutionMetadata(execution_time_ms=10.0, rows_affected=0)

        error1 = ModelError(message="Error", metadata=metadata1)
        error2 = ModelError(message="Error", metadata=metadata2)

        assert error1 == error2

    def test_with_different_causes(self) -> None:
        """Test ModelError equality with different causes."""
        metadata = ExecutionMetadata(execution_time_ms=10.0, rows_affected=0)
        error1 = ModelError(
            message="Error", metadata=metadata, cause=ValueError("cause1")
        )
        error2 = ModelError(
            message="Error", metadata=metadata, cause=ValueError("cause2")
        )

        # Different causes → different errors
        assert error1 != error2

    def test_with_none_cause(self) -> None:
        """Test ModelError with explicit None cause."""
        metadata = ExecutionMetadata(execution_time_ms=10.0, rows_affected=0)
        error = ModelError(message="Error", metadata=metadata, cause=None)

        assert error.cause is None

    def test_preserves_exception_type(self) -> None:
        """Test that ModelError preserves exception type."""
        metadata = ExecutionMetadata(execution_time_ms=10.0, rows_affected=0)

        errors = [
            ModelError(message="Error", metadata=metadata, cause=ValueError("val")),
            ModelError(message="Error", metadata=metadata, cause=TypeError("type")),
            ModelError(message="Error", metadata=metadata, cause=RuntimeError("run")),
        ]

        assert isinstance(errors[0].cause, ValueError)
        assert isinstance(errors[1].cause, TypeError)
        assert isinstance(errors[2].cause, RuntimeError)
