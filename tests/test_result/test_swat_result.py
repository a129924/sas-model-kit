"""Tests for SwatModelResult specialized container."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from sas_model_kit.result import (
    CASTableResult,
    ExecutionMetadata,
    ModelResult,
    ResultStatus,
    SwatModelResult,
)

if TYPE_CHECKING:
    from swat import CASTable


@pytest.fixture
def mock_cas_table() -> CASTable:
    """Create a mock CASTable for testing."""
    table = MagicMock()

    # Mock iterrows() to return test data
    table = MagicMock(
        to_dict=MagicMock(
            return_value=[{"id": 1, "score": 95}, {"id": 2, "score": 87}]
        ),
        __iter__=iter([{"id": 1, "score": 95}, {"id": 2, "score": 87}]),
    )

    return table


def test_swat_model_result_is_model_result() -> None:
    """Test that SwatModelResult is a ModelResult."""
    # This is a type check - SwatModelResult should be recognized as ModelResult
    assert issubclass(SwatModelResult, ModelResult)


def test_swat_model_result_from_table_default_metadata(
    mock_cas_table: CASTable,
) -> None:
    """Test creating SwatModelResult from CASTable with default metadata."""
    result = SwatModelResult.from_table(mock_cas_table)

    assert result.is_success
    assert result.status == ResultStatus.SUCCESS
    assert isinstance(result.data, CASTableResult)
    # Default metadata should have zero time and zero rows
    assert result.metadata.execution_time_ms == 0.0
    assert result.metadata.rows_affected == 0


def test_swat_model_result_from_table_with_metadata(
    mock_cas_table: CASTable,
) -> None:
    """Test creating SwatModelResult with custom metadata."""
    metadata = ExecutionMetadata(
        execution_time_ms=150.5,
        rows_affected=1000,
    )
    result = SwatModelResult.from_table(mock_cas_table, metadata=metadata)

    assert result.metadata.execution_time_ms == 150.5
    assert result.metadata.rows_affected == 1000


def test_swat_model_result_from_error_default_metadata() -> None:
    """Test creating error result with default metadata."""
    result = SwatModelResult.from_error("Table not found")

    assert result.is_error
    assert result.status == ResultStatus.ERROR
    # Default metadata should have zero time and zero rows
    assert result.metadata.execution_time_ms == 0.0
    assert result.metadata.rows_affected == 0


def test_swat_model_result_from_error_with_exception() -> None:
    """Test creating error result from exception."""
    error = ValueError("Invalid parameter")
    result = SwatModelResult.from_error(error)

    assert result.is_error
    assert result.status == ResultStatus.ERROR


def test_swat_model_result_from_error_with_metadata() -> None:
    """Test creating error result with custom metadata."""
    metadata = ExecutionMetadata(
        execution_time_ms=50.0,
        rows_affected=0,
    )
    result = SwatModelResult.from_error("Not found", metadata=metadata)

    assert result.status == ResultStatus.ERROR
    assert result.metadata.execution_time_ms == 50.0


def test_swat_model_result_get_table(mock_cas_table: CASTable) -> None:
    """Test getting underlying CASTable."""
    result = SwatModelResult.from_table(mock_cas_table)

    table = result.get_table()

    assert table is mock_cas_table


def test_swat_model_result_get_table_on_error() -> None:
    """Test that accessing table on error raises RuntimeError."""
    result = SwatModelResult.from_error("Error occurred")

    with pytest.raises(RuntimeError, match="Cannot access data on error result"):
        result.get_table()


def test_swat_model_result_to_records(mock_cas_table: CASTable) -> None:
    """Test converting result to list of records."""
    # Reset the mock's iterator for this test
    test_data = [
        (0, MagicMock(to_dict=lambda: {"id": 1, "score": 95})),
        (1, MagicMock(to_dict=lambda: {"id": 2, "score": 87})),
    ]
    mock_cas_table.iterrows.return_value = iter(test_data)

    result = SwatModelResult.from_table(mock_cas_table)

    records = result.to_records()

    assert isinstance(records, list)
    assert len(records) == 2
    assert records[0] == {"id": 1, "score": 95}
    assert records[1] == {"id": 2, "score": 87}


def test_swat_model_result_to_records_on_error() -> None:
    """Test that to_records on error raises RuntimeError."""
    result = SwatModelResult.from_error("Error occurred")

    with pytest.raises(RuntimeError, match="Cannot access data on error result"):
        result.to_records()


def test_swat_model_result_data_property_on_success(
    mock_cas_table: CASTable,
) -> None:
    """Test accessing data property on successful result."""
    result = SwatModelResult.from_table(mock_cas_table)

    data = result.data

    assert isinstance(data, CASTableResult)


def test_swat_model_result_data_property_on_error() -> None:
    """Test that accessing data property on error raises RuntimeError."""
    result = SwatModelResult.from_error("Error occurred")

    with pytest.raises(RuntimeError, match="Cannot access data on error result"):
        _ = result.data


def test_swat_model_result_iteration_via_data(
    mock_cas_table: CASTable,
) -> None:
    """Test iterating through data via the result."""
    # Reset the mock's iterator for this test
    test_data = [
        (0, MagicMock(to_dict=lambda: {"id": 1, "score": 95})),
        (1, MagicMock(to_dict=lambda: {"id": 2, "score": 87})),
    ]
    mock_cas_table.iterrows.return_value = iter(test_data)

    result = SwatModelResult.from_table(mock_cas_table)

    records = list(result.data)

    assert len(records) == 2
    assert records[0] == {"id": 1, "score": 95}


def test_swat_model_result_metadata_with_intended_output(
    mock_cas_table: CASTable,
) -> None:
    """Test SwatModelResult with intended output in metadata."""
    metadata = ExecutionMetadata(
        execution_time_ms=100.0,
        rows_affected=500,
        intended_output_caslib="public",
        intended_output_table="results",
    )
    result = SwatModelResult.from_table(mock_cas_table, metadata=metadata)

    assert result.metadata.intended_output_caslib == "public"
    assert result.metadata.intended_output_table == "results"

