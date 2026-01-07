"""Tests for DataStepParameter class."""

from __future__ import annotations

import pytest

from sas_model_kit.parameter import DataStepParameter


def test_datastep_parameter_creation() -> None:
    """Test creating a valid DataStepParameter."""
    score_code = """
    data public.output;
        set public.raw_data;
        new_var = var1 * 2;
    run;
    """
    param = DataStepParameter(
        score_code=score_code,
        output_caslib="public",
        output_table="output",
    )

    assert param.score_code == score_code
    assert param.output_caslib == "public"
    assert param.output_table == "output"


def test_datastep_parameter_simple_code() -> None:
    """Test DataStepParameter with simple inline code."""
    param = DataStepParameter(
        score_code="new_var = var1 * 2;",
        output_caslib="public",
        output_table="result",
    )

    assert param.score_code == "new_var = var1 * 2;"


def test_datastep_parameter_with_different_output_locations() -> None:
    """Test DataStepParameter with custom output locations."""
    param = DataStepParameter(
        score_code="new_var = var1 * 2;",
        output_caslib="models",
        output_table="processed_data",
    )

    assert param.output_caslib == "models"
    assert param.output_table == "processed_data"


def test_datastep_parameter_validates_score_code_not_empty() -> None:
    """Test validation that score_code is not empty."""
    param = DataStepParameter(
        score_code="",  # Invalid: empty
        output_caslib="public",
        output_table="output",
    )

    with pytest.raises(ValueError, match="score_code cannot be empty"):
        param.validate()


def test_datastep_parameter_validates_score_code_is_string() -> None:
    """Test validation that score_code is a string."""
    param = DataStepParameter(
        score_code=123,  # type: ignore[arg-type]
        output_caslib="public",
        output_table="output",
    )

    with pytest.raises(ValueError, match="score_code must be a string"):
        param.validate()


def test_datastep_parameter_validates_output_caslib_not_empty() -> None:
    """Test validation that output_caslib is not empty."""
    param = DataStepParameter(
        score_code="code",
        output_caslib="",  # Invalid: empty
        output_table="output",
    )

    with pytest.raises(ValueError, match="output_caslib cannot be empty"):
        param.validate()


def test_datastep_parameter_validates_output_table_not_empty() -> None:
    """Test validation that output_table is not empty."""
    param = DataStepParameter(
        score_code="code",
        output_caslib="public",
        output_table="",  # Invalid: empty
    )

    with pytest.raises(ValueError, match="output_table cannot be empty"):
        param.validate()


def test_datastep_parameter_successful_validation() -> None:
    """Test successful validation with valid parameters."""
    param = DataStepParameter(
        score_code="new_var = var1 * 2;",
        output_caslib="public",
        output_table="result",
    )

    # Should not raise
    param.validate()


def test_datastep_parameter_immutability() -> None:
    """Test that DataStepParameter instances are immutable."""
    param = DataStepParameter(
        score_code="new_var = var1 * 2;",
        output_caslib="public",
        output_table="result",
    )

    with pytest.raises(AttributeError):
        param.score_code = "modified"  # type: ignore[misc]


def test_datastep_parameter_equality() -> None:
    """Test equality comparison of DataStepParameter instances."""
    code = "new_var = var1 * 2;"
    param1 = DataStepParameter(
        score_code=code,
        output_caslib="public",
        output_table="result",
    )
    param2 = DataStepParameter(
        score_code=code,
        output_caslib="public",
        output_table="result",
    )
    param3 = DataStepParameter(
        score_code="new_var = var1 * 3;",
        output_caslib="public",
        output_table="result",
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
        score_code=complex_code,
        output_caslib="public",
        output_table="categorized",
    )

    assert param.score_code == complex_code
    param.validate()  # Should not raise


def test_datastep_parameter_full_datastep() -> None:
    """Test DataStepParameter with complete DATA step."""
    full_datastep = """data output_lib.output_table;
        set input_lib.input_table;
        new_var = var1 * var2;
        label new_var = 'Calculated Variable';
    run;"""

    param = DataStepParameter(
        score_code=full_datastep,
        output_caslib="output_lib",
        output_table="output_table",
    )

    assert "data output_lib.output_table" in param.score_code
    assert "set input_lib.input_table" in param.score_code
    param.validate()  # Should not raise


def test_datastep_parameter_explicit_output_location() -> None:
    """Test that DataStepParameter requires explicit output location specification."""
    # This verifies the new design - output location must be explicit
    param = DataStepParameter(
        score_code="code",
        output_caslib="public",
        output_table="result",
    )

    # Verify it has explicit output fields
    assert hasattr(param, "output_caslib")
    assert hasattr(param, "output_table")
    assert param.output_caslib == "public"
    assert param.output_table == "result"
