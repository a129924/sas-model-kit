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
    )

    assert param.source_caslib == "public"
    assert param.source_table == "input_data"
    assert param.target_caslib == "public"
    assert param.target_table == "output_data"
    assert param.model_caslib == "models"
    assert param.model_table == "my_astore"
    assert param.code_caslib == ""
    assert param.code_table == ""


def test_astore_parameter_with_code() -> None:
    """Test AstoreParameter with optional code fields."""
    param = AstoreParameter(
        source_caslib="public",
        source_table="input_data",
        target_caslib="public",
        target_table="output_data",
        model_caslib="models",
        model_table="my_astore",
        code_caslib="code_lib",
        code_table="custom_code",
    )

    assert param.code_caslib == "code_lib"
    assert param.code_table == "custom_code"


def test_astore_parameter_validates_model_caslib() -> None:
    """Test validation of model_caslib field."""
    param = AstoreParameter(
        source_caslib="public",
        source_table="input_data",
        target_caslib="public",
        target_table="output_data",
        model_caslib="",  # Invalid: empty
        model_table="my_astore",
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
    )

    with pytest.raises(ValueError, match="model_table cannot be empty"):
        param.validate()


def test_astore_parameter_validates_code_caslib_only() -> None:
    """Test validation when only code_caslib is provided."""
    param = AstoreParameter(
        source_caslib="public",
        source_table="input_data",
        target_caslib="public",
        target_table="output_data",
        model_caslib="models",
        model_table="my_astore",
        code_caslib="code_lib",  # Provided
        code_table="",  # Missing
    )

    with pytest.raises(
        ValueError,
        match="Both code_caslib and code_table must be provided together",
    ):
        param.validate()


def test_astore_parameter_validates_code_table_only() -> None:
    """Test validation when only code_table is provided."""
    param = AstoreParameter(
        source_caslib="public",
        source_table="input_data",
        target_caslib="public",
        target_table="output_data",
        model_caslib="models",
        model_table="my_astore",
        code_caslib="",  # Missing
        code_table="custom_code",  # Provided
    )

    with pytest.raises(
        ValueError,
        match="Both code_caslib and code_table must be provided together",
    ):
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
    )

    # Should not raise
    param.validate()


def test_astore_parameter_successful_validation_with_code() -> None:
    """Test successful validation with code fields."""
    param = AstoreParameter(
        source_caslib="public",
        source_table="input_data",
        target_caslib="public",
        target_table="output_data",
        model_caslib="models",
        model_table="my_astore",
        code_caslib="code_lib",
        code_table="custom_code",
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
    )

    with pytest.raises(AttributeError):
        param.model_caslib = "modified"  # type: ignore[misc]
