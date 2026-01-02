"""Tests for ExecutionMetadata class."""

from __future__ import annotations

import pytest

from sas_model_kit.result import ExecutionMetadata


def test_execution_metadata_creation() -> None:
    """Test creating ExecutionMetadata with basic fields."""
    metadata = ExecutionMetadata(
        execution_time_ms=150.5,
        rows_affected=1000,
    )

    assert metadata.execution_time_ms == 150.5
    assert metadata.rows_affected == 1000
    assert metadata.intended_output_caslib is None
    assert metadata.intended_output_table is None


def test_execution_metadata_with_intended_output() -> None:
    """Test ExecutionMetadata with intended output location."""
    metadata = ExecutionMetadata(
        execution_time_ms=250.0,
        rows_affected=0,
        intended_output_caslib="public",
        intended_output_table="results",
    )

    assert metadata.execution_time_ms == 250.0
    assert metadata.rows_affected == 0
    assert metadata.intended_output_caslib == "public"
    assert metadata.intended_output_table == "results"


def test_execution_metadata_validates_execution_time_non_negative() -> None:
    """Test validation that execution_time_ms is non-negative."""
    with pytest.raises(ValueError, match="execution_time_ms must be non-negative"):
        ExecutionMetadata(
            execution_time_ms=-1.0,
            rows_affected=0,
        )


def test_execution_metadata_validates_rows_affected_non_negative() -> None:
    """Test validation that rows_affected is non-negative."""
    with pytest.raises(ValueError, match="rows_affected must be non-negative"):
        ExecutionMetadata(
            execution_time_ms=100.0,
            rows_affected=-1,
        )


def test_execution_metadata_validates_execution_time_zero() -> None:
    """Test validation that execution_time_ms can be zero."""
    metadata = ExecutionMetadata(
        execution_time_ms=0.0,
        rows_affected=100,
    )

    assert metadata.execution_time_ms == 0.0
    # Should not raise


def test_execution_metadata_validates_rows_affected_zero() -> None:
    """Test validation that rows_affected can be zero."""
    metadata = ExecutionMetadata(
        execution_time_ms=100.0,
        rows_affected=0,
    )

    assert metadata.rows_affected == 0
    # Should not raise


def test_execution_metadata_validates_intended_output_paired() -> None:
    """Test validation that intended_output_* must be paired."""
    # Only caslib, missing table
    with pytest.raises(
        ValueError, match="intended_output_caslib and intended_output_table"
    ):
        ExecutionMetadata(
            execution_time_ms=100.0,
            rows_affected=0,
            intended_output_caslib="public",
            intended_output_table=None,
        )


def test_execution_metadata_validates_intended_output_both_non_empty() -> None:
    """Test validation that both intended_output_* are non-empty if provided."""
    # Only table, missing caslib
    with pytest.raises(
        ValueError, match="intended_output_caslib and intended_output_table"
    ):
        ExecutionMetadata(
            execution_time_ms=100.0,
            rows_affected=0,
            intended_output_caslib=None,
            intended_output_table="results",
        )


def test_execution_metadata_validates_intended_output_empty_string() -> None:
    """Test validation that intended_output_* empty strings are treated as missing."""
    # Empty string is treated as None
    with pytest.raises(
        ValueError, match="intended_output_caslib and intended_output_table"
    ):
        ExecutionMetadata(
            execution_time_ms=100.0,
            rows_affected=0,
            intended_output_caslib="",  # Empty string
            intended_output_table="results",
        )


def test_execution_metadata_immutability() -> None:
    """Test that ExecutionMetadata instances are immutable (frozen)."""
    metadata = ExecutionMetadata(
        execution_time_ms=100.0,
        rows_affected=1000,
    )

    with pytest.raises(AttributeError):
        metadata.execution_time_ms = 200.0  # type: ignore[misc]


def test_execution_metadata_equality() -> None:
    """Test equality comparison of ExecutionMetadata instances."""
    metadata1 = ExecutionMetadata(
        execution_time_ms=100.0,
        rows_affected=1000,
    )
    metadata2 = ExecutionMetadata(
        execution_time_ms=100.0,
        rows_affected=1000,
    )
    metadata3 = ExecutionMetadata(
        execution_time_ms=100.0,
        rows_affected=2000,  # Different
    )

    assert metadata1 == metadata2
    assert metadata1 != metadata3


def test_execution_metadata_large_values() -> None:
    """Test ExecutionMetadata with large numeric values."""
    metadata = ExecutionMetadata(
        execution_time_ms=1_000_000_000.5,
        rows_affected=1_000_000_000,
    )

    assert metadata.execution_time_ms == 1_000_000_000.5
    assert metadata.rows_affected == 1_000_000_000


def test_execution_metadata_precision_floats() -> None:
    """Test ExecutionMetadata with high-precision float times."""
    metadata = ExecutionMetadata(
        execution_time_ms=0.001,  # 1 microsecond
        rows_affected=1,
    )

    assert metadata.execution_time_ms == 0.001


def test_execution_metadata_with_intended_output_validation() -> None:
    """Test successful validation with intended output."""
    metadata = ExecutionMetadata(
        execution_time_ms=500.0,
        rows_affected=0,  # No actual data produced
        intended_output_caslib="models",
        intended_output_table="explain_results",
    )

    # Should not raise
    assert metadata.intended_output_caslib == "models"
    assert metadata.intended_output_table == "explain_results"
