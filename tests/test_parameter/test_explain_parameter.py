"""Tests for ExplainParameter class."""

from __future__ import annotations

import pytest

from sas_model_kit.parameter import ExplainParameter
from sas_model_kit.parameter.explain import ExplainDepth


def test_explain_parameter_creation() -> None:
    """Test creating a valid ExplainParameter."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
    )

    assert param.source_caslib == "public"
    assert param.source_table == "test_data"
    assert param.target_caslib == "public"
    assert param.target_table == "explanations"
    assert param.depth == ExplainDepth.BASIC
    assert param.generate_plots is False


def test_explain_parameter_with_depth() -> None:
    """Test ExplainParameter with custom depth."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        depth=ExplainDepth.DETAILED,
    )

    assert param.depth == ExplainDepth.DETAILED


def test_explain_parameter_with_plots() -> None:
    """Test ExplainParameter with generate_plots enabled."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        generate_plots=True,
    )

    assert param.generate_plots is True


def test_explain_parameter_full_configuration() -> None:
    """Test ExplainParameter with all options configured."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        depth=ExplainDepth.FULL,
        generate_plots=True,
    )

    assert param.depth == ExplainDepth.FULL
    assert param.generate_plots is True


def test_explain_depth_enum_values() -> None:
    """Test ExplainDepth enum values."""
    assert ExplainDepth.BASIC.value == "basic"
    assert ExplainDepth.DETAILED.value == "detailed"
    assert ExplainDepth.FULL.value == "full"


def test_explain_parameter_validates_depth_type() -> None:
    """Test validation of depth field type."""
    # Create parameter with invalid depth (not an enum)
    # This would fail at runtime if we pass wrong type
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        depth="invalid",  # type: ignore[arg-type]
    )

    with pytest.raises(ValueError, match="depth must be ExplainDepth enum"):
        param.validate()


def test_explain_parameter_successful_validation() -> None:
    """Test successful validation with all valid fields."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        depth=ExplainDepth.DETAILED,
        generate_plots=True,
    )

    # Should not raise
    param.validate()


def test_explain_parameter_validates_base_fields() -> None:
    """Test that base field validation is called."""
    param = ExplainParameter(
        source_caslib="",  # Invalid base field
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
    )

    with pytest.raises(ValueError, match="source_caslib cannot be empty"):
        param.validate()


def test_explain_parameter_immutability() -> None:
    """Test that ExplainParameter instances are immutable."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
    )

    with pytest.raises(AttributeError):
        param.depth = ExplainDepth.FULL  # type: ignore[misc]


def test_explain_parameter_equality() -> None:
    """Test equality comparison of ExplainParameter instances."""
    param1 = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        depth=ExplainDepth.DETAILED,
    )
    param2 = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        depth=ExplainDepth.DETAILED,
    )
    param3 = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        depth=ExplainDepth.FULL,  # Different
    )

    assert param1 == param2
    assert param1 != param3
