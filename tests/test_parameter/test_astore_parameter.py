"""Tests for AstoreParameter class."""

from __future__ import annotations

import pytest

from sas_model_kit.parameter import AstoreParameter


def test_astore_parameter_creation() -> None:
    """Test creating a valid AstoreParameter."""
    param = AstoreParameter(
        input_caslib="public",
        input_table="input_data",
        model_caslib="models",
        model_table="my_astore",
        score_code="proc astore; ... run;",
    )

    assert param.input_caslib == "public"
    assert param.input_table == "input_data"
    assert param.model_caslib == "models"
    assert param.model_table == "my_astore"
    assert param.score_code == "proc astore; ... run;"
    assert param.casout is None


def test_astore_parameter_with_casout() -> None:
    """Test AstoreParameter with custom casout configuration."""
    casout_config = {"name": "scored_output", "caslib": "public", "promote": True}
    param = AstoreParameter(
        input_caslib="public",
        input_table="input_data",
        model_caslib="models",
        model_table="my_astore",
        score_code="proc astore; ... run;",
        casout=casout_config,
    )

    assert param.casout == casout_config


def test_astore_parameter_validates_input_caslib() -> None:
    """Test validation of input_caslib field."""
    param = AstoreParameter(
        input_caslib="",  # Invalid: empty
        input_table="input_data",
        model_caslib="models",
        model_table="my_astore",
        score_code="proc astore; ... run;",
    )

    with pytest.raises(ValueError, match="input_caslib cannot be empty"):
        param.validate()


def test_astore_parameter_validates_input_table() -> None:
    """Test validation of input_table field."""
    param = AstoreParameter(
        input_caslib="public",
        input_table="",  # Invalid: empty
        model_caslib="models",
        model_table="my_astore",
        score_code="proc astore; ... run;",
    )

    with pytest.raises(ValueError, match="input_table cannot be empty"):
        param.validate()


def test_astore_parameter_validates_model_caslib() -> None:
    """Test validation of model_caslib field."""
    param = AstoreParameter(
        input_caslib="public",
        input_table="input_data",
        model_caslib="",  # Invalid: empty
        model_table="my_astore",
        score_code="proc astore; ... run;",
    )

    with pytest.raises(ValueError, match="model_caslib cannot be empty"):
        param.validate()


def test_astore_parameter_validates_model_table() -> None:
    """Test validation of model_table field."""
    param = AstoreParameter(
        input_caslib="public",
        input_table="input_data",
        model_caslib="models",
        model_table="",  # Invalid: empty
        score_code="proc astore; ... run;",
    )

    with pytest.raises(ValueError, match="model_table cannot be empty"):
        param.validate()


def test_astore_parameter_validates_score_code() -> None:
    """Test validation of score_code field."""
    param = AstoreParameter(
        input_caslib="public",
        input_table="input_data",
        model_caslib="models",
        model_table="my_astore",
        score_code="",  # Invalid: empty
    )

    with pytest.raises(ValueError, match="score_code cannot be empty"):
        param.validate()


def test_astore_parameter_validates_casout_dict() -> None:
    """Test validation of casout when not a dict."""
    param = AstoreParameter(
        input_caslib="public",
        input_table="input_data",
        model_caslib="models",
        model_table="my_astore",
        score_code="proc astore; ... run;",
        casout="not_a_dict",  # type: ignore[arg-type]
    )

    with pytest.raises(ValueError, match="casout must be a dictionary or None"):
        param.validate()


def test_astore_parameter_successful_validation() -> None:
    """Test successful validation with all required fields."""
    param = AstoreParameter(
        input_caslib="public",
        input_table="input_data",
        model_caslib="models",
        model_table="my_astore",
        score_code="proc astore; ... run;",
    )

    # Should not raise
    param.validate()


def test_astore_parameter_successful_validation_with_casout() -> None:
    """Test successful validation with custom casout."""
    param = AstoreParameter(
        input_caslib="public",
        input_table="input_data",
        model_caslib="models",
        model_table="my_astore",
        score_code="proc astore; ... run;",
        casout={"name": "output", "promote": True},
    )

    # Should not raise
    param.validate()


def test_astore_parameter_immutability() -> None:
    """Test that AstoreParameter instances are immutable."""
    param = AstoreParameter(
        input_caslib="public",
        input_table="input_data",
        model_caslib="models",
        model_table="my_astore",
        score_code="proc astore; ... run;",
    )

    with pytest.raises(AttributeError):
        param.input_caslib = "modified"  # type: ignore[misc]


def test_astore_parameter_equality() -> None:
    """Test equality comparison of AstoreParameter instances."""
    param1 = AstoreParameter(
        input_caslib="public",
        input_table="input_data",
        model_caslib="models",
        model_table="my_astore",
        score_code="proc astore; ... run;",
    )
    param2 = AstoreParameter(
        input_caslib="public",
        input_table="input_data",
        model_caslib="models",
        model_table="my_astore",
        score_code="proc astore; ... run;",
    )
    param3 = AstoreParameter(
        input_caslib="public",
        input_table="input_data",
        model_caslib="models",
        model_table="different_astore",  # Different
        score_code="proc astore; ... run;",
    )

    assert param1 == param2
    assert param1 != param3


def test_astore_parameter_three_layer_design() -> None:
    """Test that AstoreParameter correctly represents three layers."""
    param = AstoreParameter(
        input_caslib="public",
        input_table="raw_input",
        model_caslib="model_library",
        model_table="trained_astore",
        score_code="dcl double x1-x5; ... enddata;",
    )

    # Layer 1: Input
    assert param.input_caslib == "public"
    assert param.input_table == "raw_input"

    # Layer 2: Model
    assert param.model_caslib == "model_library"
    assert param.model_table == "trained_astore"

    # Layer 3: Score code
    assert "dcl double" in param.score_code
