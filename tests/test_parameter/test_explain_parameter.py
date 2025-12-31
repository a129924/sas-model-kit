"""Tests for ExplainParameter class."""

from __future__ import annotations

import pytest

from sas_model_kit.parameter import ExplainParameter


def test_explain_parameter_creation() -> None:
    """Test creating a valid ExplainParameter with all required fields."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="training_data",
        train_caslib="public",
        predicted_target="churn_pred",
        features=["age", "income", "tenure"],
        id_cols={"customer_id"},
        depth=2,
    )

    assert param.source_caslib == "public"
    assert param.source_table == "test_data"
    assert param.target_caslib == "public"
    assert param.target_table == "explanations"
    assert param.train_table == "training_data"
    assert param.train_caslib == "public"
    assert param.predicted_target == "churn_pred"
    assert param.features == ["age", "income", "tenure"]
    assert param.id_cols == {"customer_id"}
    assert param.depth == 2
    assert param.sas_score_code is None


def test_explain_parameter_with_sas_code() -> None:
    """Test ExplainParameter with optional SAS code."""
    sas_code = "data _temp; set input; new_var = var1 * 2; run;"
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="training_data",
        train_caslib="public",
        predicted_target="target",
        features=["f1", "f2"],
        id_cols={"id"},
        depth=3,
        sas_score_code=sas_code,
    )

    assert param.sas_score_code == sas_code


def test_explain_parameter_successful_validation() -> None:
    """Test successful validation with all valid fields."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="training_data",
        train_caslib="public",
        predicted_target="churn_pred",
        features=["age", "income", "tenure"],
        id_cols={"customer_id"},
        depth=2,
        sas_score_code="/* optional code */",
    )

    # Should not raise
    param.validate()


def test_explain_parameter_validates_train_table() -> None:
    """Test validation of train_table field."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="",  # Invalid: empty
        train_caslib="public",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=2,
    )

    with pytest.raises(ValueError, match="train_table cannot be empty"):
        param.validate()


def test_explain_parameter_validates_train_caslib() -> None:
    """Test validation of train_caslib field."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="training",
        train_caslib="",  # Invalid: empty
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=2,
    )

    with pytest.raises(ValueError, match="train_caslib cannot be empty"):
        param.validate()


def test_explain_parameter_validates_predicted_target() -> None:
    """Test validation of predicted_target field."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="training",
        train_caslib="public",
        predicted_target="",  # Invalid: empty
        features=["f1"],
        id_cols={"id"},
        depth=2,
    )

    with pytest.raises(ValueError, match="predicted_target cannot be empty"):
        param.validate()


def test_explain_parameter_validates_features_not_empty() -> None:
    """Test validation that features list is not empty."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="training",
        train_caslib="public",
        predicted_target="target",
        features=[],  # Invalid: empty list
        id_cols={"id"},
        depth=2,
    )

    with pytest.raises(ValueError, match="features cannot be empty"):
        param.validate()


def test_explain_parameter_validates_features_is_list() -> None:
    """Test validation that features is a list."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="training",
        train_caslib="public",
        predicted_target="target",
        features="not_a_list",  # type: ignore[arg-type]
        id_cols={"id"},
        depth=2,
    )

    with pytest.raises(ValueError, match="features must be a list"):
        param.validate()


def test_explain_parameter_validates_id_cols_not_empty() -> None:
    """Test validation that id_cols set is not empty."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="training",
        train_caslib="public",
        predicted_target="target",
        features=["f1"],
        id_cols=set(),  # Invalid: empty set
        depth=2,
    )

    with pytest.raises(ValueError, match="id_cols cannot be empty"):
        param.validate()


def test_explain_parameter_validates_id_cols_is_set() -> None:
    """Test validation that id_cols is a set."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="training",
        train_caslib="public",
        predicted_target="target",
        features=["f1"],
        id_cols=["not_a_set"],  # type: ignore[arg-type]
        depth=2,
    )

    with pytest.raises(ValueError, match="id_cols must be a set"):
        param.validate()


def test_explain_parameter_validates_depth_is_positive_int() -> None:
    """Test validation that depth is a positive integer."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="training",
        train_caslib="public",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=0,  # Invalid: not positive
    )

    with pytest.raises(ValueError, match="depth must be a positive int"):
        param.validate()


def test_explain_parameter_validates_depth_negative() -> None:
    """Test validation that depth cannot be negative."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="training",
        train_caslib="public",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=-1,  # Invalid: negative
    )

    with pytest.raises(ValueError, match="depth must be a positive int"):
        param.validate()


def test_explain_parameter_validates_base_fields() -> None:
    """Test that base field validation is called."""
    param = ExplainParameter(
        source_caslib="",  # Invalid base field
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="training",
        train_caslib="public",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=2,
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
        train_table="training",
        train_caslib="public",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=2,
    )

    with pytest.raises(AttributeError):
        param.depth = 5  # type: ignore[misc]


def test_explain_parameter_equality() -> None:
    """Test equality comparison of ExplainParameter instances."""
    param1 = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="training",
        train_caslib="public",
        predicted_target="target",
        features=["f1", "f2"],
        id_cols={"id"},
        depth=2,
    )
    param2 = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="training",
        train_caslib="public",
        predicted_target="target",
        features=["f1", "f2"],
        id_cols={"id"},
        depth=2,
    )
    param3 = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="training",
        train_caslib="public",
        predicted_target="target",
        features=["f1", "f2"],
        id_cols={"id"},
        depth=3,  # Different
    )

    assert param1 == param2
    assert param1 != param3


def test_explain_parameter_multiple_id_cols() -> None:
    """Test ExplainParameter with multiple ID columns."""
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="training",
        train_caslib="public",
        predicted_target="target",
        features=["f1"],
        id_cols={"customer_id", "transaction_id"},  # Multiple ID cols
        depth=2,
    )

    assert param.id_cols == {"customer_id", "transaction_id"}
    param.validate()  # Should not raise


def test_explain_parameter_multiple_features() -> None:
    """Test ExplainParameter with many feature columns."""
    features = ["age", "income", "tenure", "credit_score", "balance", "products"]
    param = ExplainParameter(
        source_caslib="public",
        source_table="test_data",
        target_caslib="public",
        target_table="explanations",
        train_table="training",
        train_caslib="public",
        predicted_target="target",
        features=features,
        id_cols={"id"},
        depth=3,
    )

    assert param.features == features
    assert len(param.features) == 6
    param.validate()  # Should not raise
