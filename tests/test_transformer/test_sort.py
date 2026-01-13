"""Tests for SortTransformer."""

from unittest.mock import Mock

import pytest

from sas_model_kit.result import Ok
from sas_model_kit.transformer.sort import SortTransformer


@pytest.fixture
def mock_operation():
    """Mock operation for testing."""
    return Mock()


@pytest.fixture
def mock_table():
    """Mock CASTable for testing."""
    table = Mock()
    table.columns = ["age", "name", "salary", "region"]
    table.sort_values = Mock(return_value=Mock())
    return table


def test_sort_single_column_ascending(mock_operation, mock_table) -> None:
    """Test sorting by single column in ascending order."""
    transformer = SortTransformer(mock_operation, by=["age"])
    result = transformer.execute(mock_table)

    # Verify sort_values was called with correct params
    mock_table.sort_values.assert_called_once_with(
        by=["age"], ascending=True, inplace=False
    )
    assert result.is_ok


def test_sort_single_column_descending(mock_operation, mock_table) -> None:
    """Test sorting by single column in descending order."""
    transformer = SortTransformer(mock_operation, by=["salary"], ascending=False)
    result = transformer.execute(mock_table)

    mock_table.sort_values.assert_called_once_with(
        by=["salary"], ascending=False, inplace=False
    )
    assert result.is_ok


def test_sort_multiple_columns(mock_operation, mock_table) -> None:
    """Test sorting by multiple columns."""
    transformer = SortTransformer(
        mock_operation, by=["region", "salary"], ascending=[True, False]
    )
    result = transformer.execute(mock_table)

    mock_table.sort_values.assert_called_once_with(
        by=["region", "salary"], ascending=[True, False], inplace=False
    )
    assert result.is_ok


def test_sort_empty_by_raises(mock_operation) -> None:
    """Test that empty by list raises error."""
    with pytest.raises(ValueError, match="cannot be empty"):
        SortTransformer(mock_operation, by=[])


def test_sort_ascending_length_mismatch_raises(mock_operation) -> None:
    """Test that ascending list length mismatch raises error."""
    with pytest.raises(ValueError, match="Length of ascending"):
        SortTransformer(
            mock_operation,
            by=["a", "b", "c"],
            ascending=[True, False],  # Only 2 elements instead of 3
        )


def test_sort_stores_operation(mock_operation, mock_table) -> None:
    """Test that transformer stores operation reference."""
    transformer = SortTransformer(mock_operation, by=["age"])
    assert transformer.operation is mock_operation


def test_sort_stores_parameters(mock_operation) -> None:
    """Test that transformer stores sort parameters."""
    transformer = SortTransformer(
        mock_operation, by=["col1", "col2"], ascending=[True, False]
    )

    assert transformer.by == ["col1", "col2"]
    assert transformer.ascending == [True, False]


def test_sort_does_not_modify_original_table(mock_operation, mock_table) -> None:
    """Test that original table is not modified (inplace=False)."""
    transformer = SortTransformer(mock_operation, by=["age"])
    result = transformer.execute(mock_table)

    # Verify inplace=False was used
    call_kwargs = mock_table.sort_values.call_args[1]
    assert call_kwargs["inplace"] is False
    assert result.is_ok


def test_sort_returns_sorted_table(mock_operation, mock_table) -> None:
    """Test that execute returns the sorted table."""
    expected_sorted = Mock()
    mock_table.sort_values.return_value = expected_sorted

    transformer = SortTransformer(mock_operation, by=["age"])
    result = transformer.execute(mock_table)

    assert result.is_ok
    assert result.value is expected_sorted


def test_sort_with_single_bool_ascending(mock_operation, mock_table) -> None:
    """Test ascending as single bool instead of list."""
    transformer = SortTransformer(
        mock_operation,
        by=["age", "name"],
        ascending=True,  # Single bool, not list
    )

    result = transformer.execute(mock_table)

    mock_table.sort_values.assert_called_once_with(
        by=["age", "name"], ascending=True, inplace=False
    )
    assert result.is_ok
