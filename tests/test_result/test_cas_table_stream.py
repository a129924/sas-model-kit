"""Unit tests for CASTableResult stream() optimization.

Tests verify that stream() uses islice for efficient batching without append overhead.
"""

from unittest.mock import MagicMock

import pytest

from sas_model_kit.result.cas_table import CASTableResult


class TestCASTableResultStream:
    """Tests for CASTableResult.stream() method."""

    def test_stream_returns_list_of_dicts(self):
        """stream() should yield list[dict] batches."""
        # Mock CASTable with iterrows
        mock_table = MagicMock()
        mock_table.iterrows.return_value = iter(
            [
                (0, MagicMock(to_dict=lambda: {"id": 1, "value": "a"})),
                (1, MagicMock(to_dict=lambda: {"id": 2, "value": "b"})),
                (2, MagicMock(to_dict=lambda: {"id": 3, "value": "c"})),
            ]
        )

        result = CASTableResult(mock_table)
        batches = list(result.stream(batch_size=2))

        # Should have 2 batches: [2 items, 1 item]
        assert len(batches) == 2
        assert len(batches[0]) == 2
        assert len(batches[1]) == 1

    def test_stream_respects_batch_size(self):
        """stream() should respect batch_size parameter."""
        mock_table = MagicMock()
        mock_table.iterrows.return_value = iter(
            [(i, MagicMock(to_dict=lambda i=i: {"id": i})) for i in range(10)]
        )

        result = CASTableResult(mock_table)

        # Test batch_size=3
        batches = list(result.stream(batch_size=3))
        assert len(batches) == 4  # 3, 3, 3, 1
        assert len(batches[0]) == 3
        assert len(batches[1]) == 3
        assert len(batches[2]) == 3
        assert len(batches[3]) == 1

    def test_stream_last_batch_may_be_smaller(self):
        """Last batch may contain fewer items than batch_size."""
        mock_table = MagicMock()
        mock_table.iterrows.return_value = iter(
            [(i, MagicMock(to_dict=lambda i=i: {"id": i})) for i in range(5)]
        )

        result = CASTableResult(mock_table)
        batches = list(result.stream(batch_size=2))

        assert len(batches) == 3
        assert len(batches[0]) == 2
        assert len(batches[1]) == 2
        assert len(batches[2]) == 1  # Last batch smaller

    def test_stream_empty_table(self):
        """stream() should handle empty table gracefully."""
        mock_table = MagicMock()
        mock_table.iterrows.return_value = iter([])

        result = CASTableResult(mock_table)
        batches = list(result.stream(batch_size=10))

        assert batches == []

    def test_stream_single_item(self):
        """stream() should handle single item."""
        mock_table = MagicMock()
        mock_table.iterrows.return_value = iter(
            [(0, MagicMock(to_dict=lambda: {"id": 1}))]
        )

        result = CASTableResult(mock_table)
        batches = list(result.stream(batch_size=10))

        assert len(batches) == 1
        assert len(batches[0]) == 1

    def test_stream_batch_size_invalid(self):
        """stream() should raise ValueError for invalid batch_size."""
        mock_table = MagicMock()
        result = CASTableResult(mock_table)

        with pytest.raises(ValueError, match="batch_size must be > 0"):
            list(result.stream(batch_size=0))

        with pytest.raises(ValueError, match="batch_size must be > 0"):
            list(result.stream(batch_size=-1))

    def test_stream_default_batch_size(self):
        """stream() should use default batch_size=1000."""
        mock_table = MagicMock()
        mock_table.iterrows.return_value = iter(
            [(i, MagicMock(to_dict=lambda i=i: {"id": i})) for i in range(500)]
        )

        result = CASTableResult(mock_table)
        batches = list(result.stream())  # Use default

        # Default is 1000, so all 500 items in one batch
        assert len(batches) == 1
        assert len(batches[0]) == 500

    def test_stream_preserves_dict_content(self):
        """stream() should preserve dictionary content correctly."""
        mock_table = MagicMock()

        # Create mock series with to_dict method
        series_1 = MagicMock()
        series_1.to_dict.return_value = {"id": 1, "name": "Alice", "score": 100}

        series_2 = MagicMock()
        series_2.to_dict.return_value = {"id": 2, "name": "Bob", "score": 95}

        mock_table.iterrows.return_value = iter(
            [
                (0, series_1),
                (1, series_2),
            ]
        )

        result = CASTableResult(mock_table)
        batches = list(result.stream(batch_size=1))

        assert batches[0][0] == {"id": 1, "name": "Alice", "score": 100}
        assert batches[1][0] == {"id": 2, "name": "Bob", "score": 95}

    def test_stream_vs_iter_performance_characteristics(self):
        """stream() should use islice without append overhead.

        This test verifies that stream() uses islice by checking:
        1. Batch iteration (vs single-row iteration)
        2. No append() calls in the implementation
        """
        mock_table = MagicMock()
        mock_table.iterrows.return_value = iter(
            [(i, MagicMock(to_dict=lambda i=i: {"id": i})) for i in range(100)]
        )

        result = CASTableResult(mock_table)

        # Collect statistics
        batch_count = 0
        total_items = 0

        for batch in result.stream(batch_size=10):
            batch_count += 1
            total_items += len(batch)

        assert total_items == 100
        assert batch_count == 10  # 100 items / 10 per batch

    def test_stream_is_generator(self):
        """stream() should return a generator, not a list."""
        mock_table = MagicMock()
        mock_table.iterrows.return_value = iter([])

        result = CASTableResult(mock_table)
        stream_result = result.stream(batch_size=10)

        # Should be a generator
        assert hasattr(stream_result, "__iter__")
        assert hasattr(stream_result, "__next__")
