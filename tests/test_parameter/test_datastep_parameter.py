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
    param = DataStepParameter(score_code=score_code)

    assert param.score_code == score_code
    assert param.casout is None


def test_datastep_parameter_simple_code() -> None:
    """Test DataStepParameter with simple inline code."""
    param = DataStepParameter(score_code="new_var = var1 * 2;")

    assert param.score_code == "new_var = var1 * 2;"


def test_datastep_parameter_with_casout() -> None:
    """Test DataStepParameter with custom casout configuration."""
    casout_config = {"name": "override_output", "caslib": "public"}
    param = DataStepParameter(
        score_code="new_var = var1 * 2;",
        casout=casout_config,
    )

    assert param.casout == casout_config


def test_datastep_parameter_validates_score_code_not_empty() -> None:
    """Test validation that score_code is not empty."""
    param = DataStepParameter(
        score_code="",  # Invalid: empty
    )

    with pytest.raises(ValueError, match="score_code cannot be empty"):
        param.validate()


def test_datastep_parameter_validates_score_code_is_string() -> None:
    """Test validation that score_code is a string."""
    param = DataStepParameter(
        score_code=123,  # type: ignore[arg-type]
    )

    with pytest.raises(ValueError, match="score_code must be a string"):
        param.validate()


def test_datastep_parameter_validates_casout_dict() -> None:
    """Test validation that casout is a dict or None."""
    param = DataStepParameter(
        score_code="new_var = var1 * 2;",
        casout="not_a_dict",  # type: ignore[arg-type]
    )

    with pytest.raises(ValueError, match="casout must be a dictionary or None"):
        param.validate()


def test_datastep_parameter_successful_validation() -> None:
    """Test successful validation with valid score_code."""
    param = DataStepParameter(score_code="new_var = var1 * 2;")

    # Should not raise
    param.validate()


def test_datastep_parameter_successful_validation_with_casout() -> None:
    """Test successful validation with casout."""
    param = DataStepParameter(
        score_code="new_var = var1 * 2;",
        casout={"name": "output", "promote": True},
    )

    # Should not raise
    param.validate()


def test_datastep_parameter_immutability() -> None:
    """Test that DataStepParameter instances are immutable."""
    param = DataStepParameter(score_code="new_var = var1 * 2;")

    with pytest.raises(AttributeError):
        param.score_code = "modified"  # type: ignore[misc]


def test_datastep_parameter_equality() -> None:
    """Test equality comparison of DataStepParameter instances."""
    code = "new_var = var1 * 2;"
    param1 = DataStepParameter(score_code=code)
    param2 = DataStepParameter(score_code=code)
    param3 = DataStepParameter(score_code="new_var = var1 * 3;")

    assert param1 == param2
    assert param1 != param3


def test_datastep_parameter_complex_code() -> None:
    """Test DataStepParameter with complex multi-line code."""
    complex_code = """if var1 > 10 then category = 'high';
    else if var1 > 5 then category = 'medium';
    else category = 'low';
    new_var = var1 * var2;"""

    param = DataStepParameter(score_code=complex_code)

    assert param.score_code == complex_code
    param.validate()  # Should not raise


def test_datastep_parameter_full_datastep() -> None:
    """Test DataStepParameter with complete DATA step."""
    full_datastep = """data output_lib.output_table;
        set input_lib.input_table;
        new_var = var1 * var2;
        label new_var = 'Calculated Variable';
    run;"""

    param = DataStepParameter(score_code=full_datastep)

    assert "data output_lib.output_table" in param.score_code
    assert "set input_lib.input_table" in param.score_code
    param.validate()  # Should not raise


def test_datastep_parameter_minimal_responsibility() -> None:
    """Test that DataStepParameter has minimal fields (only score_code and optional casout)."""
    # This verifies SRP - DataStepParameter only has what it needs
    param = DataStepParameter(score_code="code")

    # Verify it doesn't have input_*/output_* like old design
    assert not hasattr(param, "source_caslib")
    assert not hasattr(param, "source_table")
    assert not hasattr(param, "target_caslib")
    assert not hasattr(param, "target_table")

    # Verify it only has score_code and casout
    assert hasattr(param, "score_code")
    assert hasattr(param, "casout")
