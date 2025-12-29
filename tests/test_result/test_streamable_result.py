"""
Unit tests for StreamableResult protocol.

Tests verify that implementations of StreamableResult protocol
work correctly.
"""

from typing import Iterator

import pytest

from sas_model_kit.result.streamable import StreamableResult


class MockStreamableResult:
    """Mock implementation of StreamableResult for testing."""

    def __init__(self, data: list[dict]):
        """Initialize with test data."""
        self._data = data

    def __iter__(self) -> Iterator[dict]:
        """Iterate over rows."""
        for row in self._data:
            yield row

    def stream(self, batch_size: int = 1000) -> Iterator[dict]:
        """Stream rows in batches."""
        for row in self._data:
            yield row

    def to_records(self) -> list[dict]:
        """Convert to list of records."""
        return self._data.copy()


class TestStreamableResultProtocol:
    """Test StreamableResult protocol compliance."""

    def test_mock_implements_protocol(self):
        """Mock should implement StreamableResult protocol."""
        # Arrange
        data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        result = MockStreamableResult(data)

        # Act & Assert - no TypeError means protocol is satisfied
        assert isinstance(result, StreamableResult)

    def test_iter_returns_iterator(self):
        """__iter__() should return an iterator."""
        # Arrange
        data = [{"a": 1}, {"a": 2}]
        result = MockStreamableResult(data)

        # Act
        iterator = iter(result)

        # Assert
        assert hasattr(iterator, "__next__")

    def test_iter_yields_rows(self):
        """__iter__() should yield each row."""
        # Arrange
        data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        result = MockStreamableResult(data)

        # Act
        rows = list(result)

        # Assert
        assert rows == data

    def test_stream_yields_rows(self):
        """stream() should yield rows."""
        # Arrange
        data = [{"a": 1}, {"a": 2}, {"a": 3}]
        result = MockStreamableResult(data)

        # Act
        rows = list(result.stream(batch_size=2))

        # Assert
        assert rows == data

    def test_to_records_returns_list(self):
        """to_records() should return list of dicts."""
        # Arrange
        data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        result = MockStreamableResult(data)

        # Act
        records = result.to_records()

        # Assert
        assert isinstance(records, list)
        assert records == data

    def test_to_records_creates_copy(self):
        """to_records() should return a copy, not the original."""
        # Arrange
        data = [{"a": 1}]
        result = MockStreamableResult(data)

        # Act
        records = result.to_records()
        records.append({"a": 2})

        # Assert - original should not be modified
        assert len(result._data) == 1
        assert len(records) == 2
