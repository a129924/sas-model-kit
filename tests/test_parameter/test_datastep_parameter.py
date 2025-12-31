"""Tests for DataStepParameter class."""

from __future__ import annotations

import pytest

from sas_model_kit.parameter import DataStepParameter


def test_datastep_parameter_creation() -> None:
    """Test creating a valid DataStepParameter."""
    param = DataStepParameter(
        source_caslib="public",
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        score_code="new_var = var1 * 2;",
    )

    assert param.source_caslib == "public"
    assert param.source_table == "raw_data"
    assert param.target_caslib == "public"
    assert param.target_table == "processed_data"
    assert param.score_code == "new_var = var1 * 2;"


def test_datastep_parameter_validates_score_code() -> None:
    """Test validation of score_code field."""
    param = DataStepParameter(
        source_caslib="public",
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        score_code="",  # Invalid: empty
    )

    with pytest.raises(ValueError, match="score_code cannot be empty"):
        param.validate()


def test_datastep_parameter_successful_validation() -> None:
    """Test successful validation with all valid fields."""
    param = DataStepParameter(
        source_caslib="public",
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        score_code="new_var = var1 * 2;",
    )

    # Should not raise
    param.validate()


def test_datastep_parameter_validates_base_fields() -> None:
    """Test that base field validation is called."""
    param = DataStepParameter(
        source_caslib="",  # Invalid base field
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        score_code="new_var = var1 * 2;",
    )

    with pytest.raises(ValueError, match="source_caslib cannot be empty"):
        param.validate()


def test_datastep_parameter_immutability() -> None:
    """Test that DataStepParameter instances are immutable."""
    param = DataStepParameter(
        source_caslib="public",
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        score_code="new_var = var1 * 2;",
    )

    with pytest.raises(AttributeError):
        param.score_code = "modified"  # type: ignore[misc]


def test_datastep_parameter_equality() -> None:
    """Test equality comparison of DataStepParameter instances."""
    param1 = DataStepParameter(
        source_caslib="public",
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        score_code="new_var = var1 * 2;",
    )
    param2 = DataStepParameter(
        source_caslib="public",
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        score_code="new_var = var1 * 2;",
    )
    param3 = DataStepParameter(
        source_caslib="public",
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        score_code="new_var = var1 * 3;",  # Different
    )

    assert param1 == param2
    assert param1 != param3


def test_datastep_parameter_complex_code() -> None:
    """Test DataStepParameter with complex multi-line code."""
    complex_code = """if var1 > 10 then category = 'high';
    else if var1 > 5 then category = 'medium';
    else category = 'low';
    new_var = var1 * var2;"""

    param = DataStepParameter(
        source_caslib="public",
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        score_code=complex_code,
    )

    assert param.score_code == complex_code
    param.validate()  # Should not raise
