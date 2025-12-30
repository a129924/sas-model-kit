"""Tests for CASTableResult wrapper implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from sas_model_kit.result import CASTableResult, StreamableResult

if TYPE_CHECKING:
    from swat import CASTable


@pytest.fixture
def mock_cas_table() -> CASTable:
    """Create a mock CASTable for testing."""
    table = MagicMock()

    # Mock iterrows() to return test data
    test_data = [
        (0, MagicMock(to_dict=lambda any_key=None: {"id": 1, "name": "Alice"})),
        (1, MagicMock(to_dict=lambda any_key=None: {"id": 2, "name": "Bob"})),
        (2, MagicMock(to_dict=lambda any_key=None: {"id": 3, "name": "Charlie"})),
    ]

    table.iterrows.return_value = iter(test_data)

    return table


def test_cas_table_result_is_streamable_result(
    mock_cas_table: CASTable,
) -> None:
    """Test that CASTableResult implements StreamableResult protocol."""
    result = CASTableResult(mock_cas_table)
    assert isinstance(result, StreamableResult)


def test_cas_table_result_table_property(mock_cas_table: CASTable) -> None:
    """Test access to underlying CASTable."""
    result = CASTableResult(mock_cas_table)
    assert result.table is mock_cas_table


def test_cas_table_result_iteration(mock_cas_table: CASTable) -> None:
    """Test iteration over table records."""
    result = CASTableResult(mock_cas_table)

    records = list(result)

    assert len(records) == 3
    assert records[0] == {"id": 1, "name": "Alice"}
    assert records[1] == {"id": 2, "name": "Bob"}
    assert records[2] == {"id": 3, "name": "Charlie"}


def test_cas_table_result_stream(mock_cas_table: CASTable) -> None:
    """Test streaming with batch size."""
    result = CASTableResult(mock_cas_table)

    # Stream with batch_size=2 should yield first 2 records
    batches = list(result.stream(batch_size=2))

    assert len(batches) == 2
    assert batches[0][0] == {"id": 1, "name": "Alice"}
    assert batches[0][1] == {"id": 2, "name": "Bob"}


def test_cas_table_result_stream_default_batch(
    mock_cas_table: CASTable,
) -> None:
    """Test streaming with default batch size."""
    result = CASTableResult(mock_cas_table)

    # With default batch_size=1000, should get all 3 records
    records = list(result.stream())

    assert len(records) == 3


def test_cas_table_result_to_records(mock_cas_table: CASTable) -> None:
    """Test conversion to list of dictionaries."""
    result = CASTableResult(mock_cas_table)

    records = result.to_records()

    assert isinstance(records, list)
    assert len(records) == 3
    assert records[0] == {"id": 1, "name": "Alice"}
    assert records[1] == {"id": 2, "name": "Bob"}
    assert records[2] == {"id": 3, "name": "Charlie"}


def test_cas_table_result_multiple_iterations(
    mock_cas_table: CASTable,
) -> None:
    """Test that result can be iterated multiple times."""
    result = CASTableResult(mock_cas_table)

    # First iteration
    records1 = list(result)
    # Need to reset the mock's iterator for second iteration
    test_data = [
        (0, MagicMock(to_dict=lambda: {"id": 1, "name": "Alice"})),
        (1, MagicMock(to_dict=lambda: {"id": 2, "name": "Bob"})),
        (2, MagicMock(to_dict=lambda: {"id": 3, "name": "Charlie"})),
    ]
    mock_cas_table.iterrows.return_value = iter(test_data)

    # Second iteration
    records2 = list(result)

    assert records1 == records2
