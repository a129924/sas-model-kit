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
        code="data output; set input; run;",
    )

    assert param.source_caslib == "public"
    assert param.source_table == "raw_data"
    assert param.target_caslib == "public"
    assert param.target_table == "processed_data"
    assert param.code == "data output; set input; run;"
    assert param.max_threads == 1


def test_datastep_parameter_with_threads() -> None:
    """Test DataStepParameter with custom max_threads."""
    param = DataStepParameter(
        source_caslib="public",
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        code="data output; set input; run;",
        max_threads=4,
    )

    assert param.max_threads == 4


def test_datastep_parameter_validates_code() -> None:
    """Test validation of code field."""
    param = DataStepParameter(
        source_caslib="public",
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        code="",  # Invalid: empty
    )

    with pytest.raises(ValueError, match="code cannot be empty"):
        param.validate()


def test_datastep_parameter_validates_max_threads_positive() -> None:
    """Test validation of max_threads must be positive."""
    param = DataStepParameter(
        source_caslib="public",
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        code="data output; set input; run;",
        max_threads=0,  # Invalid: must be >= 1
    )

    with pytest.raises(ValueError, match="max_threads must be >= 1"):
        param.validate()


def test_datastep_parameter_validates_max_threads_negative() -> None:
    """Test validation of max_threads cannot be negative."""
    param = DataStepParameter(
        source_caslib="public",
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        code="data output; set input; run;",
        max_threads=-1,  # Invalid: must be >= 1
    )

    with pytest.raises(ValueError, match="max_threads must be >= 1"):
        param.validate()


def test_datastep_parameter_successful_validation() -> None:
    """Test successful validation with all valid fields."""
    param = DataStepParameter(
        source_caslib="public",
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        code="data output; set input; new_var = var1 * 2; run;",
        max_threads=4,
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
        code="data output; set input; run;",
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
        code="data output; set input; run;",
    )

    with pytest.raises(AttributeError):
        param.code = "modified"  # type: ignore[misc]


def test_datastep_parameter_equality() -> None:
    """Test equality comparison of DataStepParameter instances."""
    param1 = DataStepParameter(
        source_caslib="public",
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        code="data output; set input; run;",
        max_threads=4,
    )
    param2 = DataStepParameter(
        source_caslib="public",
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        code="data output; set input; run;",
        max_threads=4,
    )
    param3 = DataStepParameter(
        source_caslib="public",
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        code="data output; set input; run;",
        max_threads=8,  # Different
    )

    assert param1 == param2
    assert param1 != param3


def test_datastep_parameter_complex_code() -> None:
    """Test DataStepParameter with complex multi-line code."""
    complex_code = """
    data output;
        set input;
        if var1 > 10 then category = 'high';
        else if var1 > 5 then category = 'medium';
        else category = 'low';
        new_var = var1 * var2;
    run;
    """

    param = DataStepParameter(
        source_caslib="public",
        source_table="raw_data",
        target_caslib="public",
        target_table="processed_data",
        code=complex_code,
        max_threads=2,
    )

    assert param.code == complex_code
    param.validate()  # Should not raise
