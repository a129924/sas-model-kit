"""Tests for ModelResult generic container."""

import pytest

from sas_model_kit.result import (
    ExecutionMetadata,
    ModelResult,
    ResultStatus,
    StreamableResult,
)


class MockStreamable(StreamableResult):
    """Mock StreamableResult for testing."""

    def __iter__(self):
        """Iterate over mock data."""
        return iter([{"id": 1}, {"id": 2}])

    def stream(self, batch_size: int = 1000):
        """Stream mock data."""
        return iter([[{"id": 1}, {"id": 2}]])

    def to_records(self) -> list[dict]:
        """Convert to records."""
        return [{"id": 1}, {"id": 2}]


def test_model_result_with_success_status_and_data() -> None:
    """Test creating a successful ModelResult with data."""
    data = MockStreamable()
    metadata = ExecutionMetadata(
        execution_time_ms=150.0,
        rows_affected=100,
    )
    result = ModelResult(
        status=ResultStatus.SUCCESS,
        data=data,
        metadata=metadata,
    )

    assert result.status == ResultStatus.SUCCESS
    assert result.data is data
    assert result.metadata == metadata
    assert result.metadata.execution_time_ms == 150.0


def test_model_result_with_error_status() -> None:
    """Test creating an error ModelResult."""
    metadata = ExecutionMetadata(
        execution_time_ms=50.0,
        rows_affected=0,
    )
    result = ModelResult(
        status=ResultStatus.ERROR,
        data=None,
        metadata=metadata,
    )

    assert result.status == ResultStatus.ERROR
    assert result.data is None
    assert result.metadata.execution_time_ms == 50.0


def test_model_result_with_no_data_output() -> None:
    """Test ModelResult without data (no-data scenario)."""
    metadata = ExecutionMetadata(
        execution_time_ms=250.0,
        rows_affected=0,
        intended_output_caslib="models",
        intended_output_table="explain_results",
    )
    result = ModelResult(
        status=ResultStatus.SUCCESS,
        data=None,
        metadata=metadata,
    )

    assert result.status == ResultStatus.SUCCESS
    assert result.data is None
    assert result.metadata.intended_output_caslib == "models"
    assert result.metadata.intended_output_table == "explain_results"


def test_model_result_with_streamable_data() -> None:
    """Test ModelResult with StreamableResult data."""
    streamable = MockStreamable()
    metadata = ExecutionMetadata(
        execution_time_ms=100.0,
        rows_affected=1000,
    )
    result = ModelResult(
        status=ResultStatus.SUCCESS,
        data=streamable,
        metadata=metadata,
    )

    assert result.status == ResultStatus.SUCCESS
    assert isinstance(result.data, StreamableResult)
    assert result.is_success is True


def test_model_result_is_success_property() -> None:
    """Test is_success convenience property."""
    metadata = ExecutionMetadata(
        execution_time_ms=100.0,
        rows_affected=100,
    )

    success_result = ModelResult(
        status=ResultStatus.SUCCESS,
        data=MockStreamable(),
        metadata=metadata,
    )
    error_result = ModelResult(
        status=ResultStatus.ERROR,
        data=None,
        metadata=metadata,
    )

    assert success_result.is_success is True
    assert error_result.is_success is False


def test_model_result_is_error_property() -> None:
    """Test is_error convenience property."""
    metadata = ExecutionMetadata(
        execution_time_ms=100.0,
        rows_affected=0,
    )

    success_result = ModelResult(
        status=ResultStatus.SUCCESS,
        data=MockStreamable(),
        metadata=metadata,
    )
    error_result = ModelResult(
        status=ResultStatus.ERROR,
        data=None,
        metadata=metadata,
    )

    assert success_result.is_error is False
    assert error_result.is_error is True


def test_model_result_requires_execution_metadata() -> None:
    """Test that ModelResult requires ExecutionMetadata."""
    with pytest.raises(TypeError, match="metadata must be ExecutionMetadata"):
        ModelResult(
            status=ResultStatus.SUCCESS,
            data=MockStreamable(),
            metadata={"rows": 100},  # type: ignore[arg-type]
        )


def test_model_result_metadata_access() -> None:
    """Test accessing ExecutionMetadata fields through ModelResult."""
    metadata = ExecutionMetadata(
        execution_time_ms=123.45,
        rows_affected=567,
    )
    result = ModelResult(
        status=ResultStatus.SUCCESS,
        data=None,
        metadata=metadata,
    )

    assert result.metadata.execution_time_ms == 123.45
    assert result.metadata.rows_affected == 567


def test_model_result_generic_type_mockstreamable() -> None:
    """Test ModelResult with StreamableResult generic type."""
    data = MockStreamable()
    metadata = ExecutionMetadata(
        execution_time_ms=100.0,
        rows_affected=100,
    )
    result: ModelResult[MockStreamable] = ModelResult(
        status=ResultStatus.SUCCESS,
        data=data,
        metadata=metadata,
    )

    assert result.data is data
    assert isinstance(result.data, StreamableResult)


def test_model_result_data_none_with_string_type() -> None:
    """Test ModelResult with None data (type allows None)."""
    metadata = ExecutionMetadata(
        execution_time_ms=100.0,
        rows_affected=0,
    )
    result: ModelResult[str] = ModelResult(
        status=ResultStatus.SUCCESS,
        data=None,  # Allowed: data is Optional
        metadata=metadata,
    )

    assert result.data is None
    assert result.is_success is True


def test_model_result_with_large_execution_time() -> None:
    """Test ModelResult with large execution time."""
    metadata = ExecutionMetadata(
        execution_time_ms=1_000_000.5,
        rows_affected=1_000_000,
    )
    result = ModelResult(
        status=ResultStatus.SUCCESS,
        data=None,
        metadata=metadata,
    )

    assert result.metadata.execution_time_ms == 1_000_000.5
    assert result.metadata.rows_affected == 1_000_000


def test_model_result_with_zero_execution_time() -> None:
    """Test ModelResult with zero execution time."""
    metadata = ExecutionMetadata(
        execution_time_ms=0.0,
        rows_affected=0,
    )
    result = ModelResult(
        status=ResultStatus.SUCCESS,
        data=None,
        metadata=metadata,
    )

    assert result.metadata.execution_time_ms == 0.0
    assert result.is_success is True
