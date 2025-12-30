"""Tests for SwatModelResult specialized container."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from sas_model_kit.result import (
    CASTableResult,
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


def test_swat_model_result_from_table(mock_cas_table: CASTable) -> None:
    """Test creating SwatModelResult from CASTable."""
    result = SwatModelResult.from_table(mock_cas_table)

    assert result.is_success
    assert result.status == ResultStatus.SUCCESS
    assert isinstance(result.data, CASTableResult)


def test_swat_model_result_from_table_with_metadata(
    mock_cas_table: CASTable,
) -> None:
    """Test creating SwatModelResult with metadata."""
    metadata = {"model": "decision_tree", "accuracy": 0.95}
    result = SwatModelResult.from_table(mock_cas_table, metadata=metadata)

    assert result.metadata["model"] == "decision_tree"
    assert result.metadata["accuracy"] == 0.95


def test_swat_model_result_from_error_with_string() -> None:
    """Test creating error result from string."""
    result = SwatModelResult.from_error("Table not found")

    assert result.is_error
    assert result.status == ResultStatus.ERROR
    assert result.metadata["error"] == "Table not found"


def test_swat_model_result_from_error_with_exception() -> None:
    """Test creating error result from exception."""
    error = ValueError("Invalid parameter")
    result = SwatModelResult.from_error(error)

    assert result.is_error
    assert result.status == ResultStatus.ERROR
    assert "Invalid parameter" in result.metadata["error"]


def test_swat_model_result_from_error_with_metadata() -> None:
    """Test creating error result with custom metadata."""
    metadata = {"table": "missing_table", "operation": "score"}
    result = SwatModelResult.from_error("Not found", metadata=metadata)

    assert result.metadata["error"] == "Not found"
    assert result.metadata["table"] == "missing_table"
    assert result.metadata["operation"] == "score"


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
