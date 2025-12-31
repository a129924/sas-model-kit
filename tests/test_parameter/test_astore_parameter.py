"""Tests for AstoreParameter class."""

from __future__ import annotations

import pytest

from sas_model_kit.parameter import AstoreParameter


def test_astore_parameter_creation() -> None:
    """Test creating a valid AstoreParameter."""
    param = AstoreParameter(
        source_caslib="public",
        source_table="input_data",
        target_caslib="public",
        target_table="output_data",
        model_caslib="models",
        model_table="my_astore",
        score_code="proc astore; ... run;",
    )

    assert param.source_caslib == "public"
    assert param.source_table == "input_data"
    assert param.target_caslib == "public"
    assert param.target_table == "output_data"
    assert param.model_caslib == "models"
    assert param.model_table == "my_astore"
    assert param.score_code == "proc astore; ... run;"


def test_astore_parameter_with_score_code() -> None:
    """Test AstoreParameter with score_code field."""
    param = AstoreParameter(
        source_caslib="public",
        source_table="input_data",
        target_caslib="public",
        target_table="output_data",
        model_caslib="models",
        model_table="my_astore",
        score_code="data _astore_input_; set input; run;",
    )

    assert param.score_code == "data _astore_input_; set input; run;"


def test_astore_parameter_validates_model_caslib() -> None:
    """Test validation of model_caslib field."""
    param = AstoreParameter(
        source_caslib="public",
        source_table="input_data",
        target_caslib="public",
        target_table="output_data",
        model_caslib="",  # Invalid: empty
        model_table="my_astore",
        score_code="proc astore; ... run;",
    )

    with pytest.raises(ValueError, match="model_caslib cannot be empty"):
        param.validate()


def test_astore_parameter_validates_model_table() -> None:
    """Test validation of model_table field."""
    param = AstoreParameter(
        source_caslib="public",
        source_table="input_data",
        target_caslib="public",
        target_table="output_data",
        model_caslib="models",
        model_table="",  # Invalid: empty
        score_code="proc astore; ... run;",
    )

    with pytest.raises(ValueError, match="model_table cannot be empty"):
        param.validate()


def test_astore_parameter_validates_score_code() -> None:
    """Test validation of score_code field."""
    param = AstoreParameter(
        source_caslib="public",
        source_table="input_data",
        target_caslib="public",
        target_table="output_data",
        model_caslib="models",
        model_table="my_astore",
        score_code="",  # Invalid: empty
    )

    with pytest.raises(ValueError, match="score_code cannot be empty"):
        param.validate()


def test_astore_parameter_successful_validation() -> None:
    """Test successful validation with all required fields."""
    param = AstoreParameter(
        source_caslib="public",
        source_table="input_data",
        target_caslib="public",
        target_table="output_data",
        model_caslib="models",
        model_table="my_astore",
        score_code="proc astore; ... run;",
    )

    # Should not raise
    param.validate()


def test_astore_parameter_successful_validation_with_score_code() -> None:
    """Test successful validation with score_code field."""
    param = AstoreParameter(
        source_caslib="public",
        source_table="input_data",
        target_caslib="public",
        target_table="output_data",
        model_caslib="models",
        model_table="my_astore",
        score_code="data _astore_input_; set input; run;",
    )

    # Should not raise
    param.validate()


def test_astore_parameter_validates_base_fields() -> None:
    """Test that base field validation is called."""
    param = AstoreParameter(
        source_caslib="",  # Invalid base field
        source_table="input_data",
        target_caslib="public",
        target_table="output_data",
        model_caslib="models",
        model_table="my_astore",
        score_code="proc astore; ... run;",
    )

    with pytest.raises(ValueError, match="source_caslib cannot be empty"):
        param.validate()


def test_astore_parameter_immutability() -> None:
    """Test that AstoreParameter instances are immutable."""
    param = AstoreParameter(
        source_caslib="public",
        source_table="input_data",
        target_caslib="public",
        target_table="output_data",
        model_caslib="models",
        model_table="my_astore",
        score_code="proc astore; ... run;",
    )

    with pytest.raises(AttributeError):
        param.model_caslib = "modified"  # type: ignore[misc]
