"""Tests for ExplainParameter class."""

from __future__ import annotations

import pytest

from sas_model_kit.model.types import ModelTableType
from sas_model_kit.parameter import ExplainParameter


def test_explain_parameter_creation_minimal_astore() -> None:
    """Test creating ExplainParameter with minimal required fields for ASTORE."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="churn_pred",
        features=["age", "income", "tenure"],
        id_cols={"customer_id"},
        depth=2,
        model_caslib="models",
        model_table="my_astore",
        sas_score_code="dcl package astore; ...",
        model_table_type=ModelTableType.ASTORE,
    )

    assert param.train_caslib == "public"
    assert param.train_table == "training_data"
    assert param.predicted_target == "churn_pred"
    assert param.features == ["age", "income", "tenure"]
    assert param.id_cols == {"customer_id"}
    assert param.depth == 2
    assert param.model_caslib == "models"
    assert param.model_table == "my_astore"
    assert param.sas_score_code == "dcl package astore; ..."


def test_explain_parameter_creation_with_datastep() -> None:
    """Test creating ExplainParameter with DataStep model."""
    sas_code = "new_var = var1 * var2;"
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1", "f2"],
        id_cols={"id"},
        depth=1,
        sas_score_code=sas_code,
        model_caslib="models",
        model_table="model_ref",
        model_table_type=ModelTableType.DATASTEP,
    )

    assert param.train_caslib == "public"
    assert param.train_table == "training_data"
    assert param.sas_score_code == sas_code
    assert param.model_table_type == ModelTableType.DATASTEP


def test_explain_parameter_validates_train_caslib() -> None:
    """Test validation of train_caslib."""
    param = ExplainParameter(
        train_caslib="",  # Invalid: empty
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    with pytest.raises(ValueError, match="train_caslib"):
        param.validate()


def test_explain_parameter_validates_train_table() -> None:
    """Test validation of train_table."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="",  # Invalid: empty
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    with pytest.raises(ValueError, match="train_table"):
        param.validate()


def test_explain_parameter_validates_predicted_target() -> None:
    """Test validation of predicted_target."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="",  # Invalid: empty
        features=["f1"],
        id_cols={"id"},
        depth=1,
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    with pytest.raises(ValueError, match="predicted_target"):
        param.validate()


def test_explain_parameter_validates_features_not_empty() -> None:
    """Test validation that features list is not empty."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=[],  # Invalid: empty list
        id_cols={"id"},
        depth=1,
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    with pytest.raises(ValueError, match="features"):
        param.validate()


def test_explain_parameter_validates_features_is_list() -> None:
    """Test validation that features is a list."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features="not_a_list",  # type: ignore[arg-type]
        id_cols={"id"},
        depth=1,
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    with pytest.raises(ValueError, match="features"):
        param.validate()


def test_explain_parameter_validates_id_cols_not_empty() -> None:
    """Test validation that id_cols set is not empty."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols=set(),  # Invalid: empty set
        depth=1,
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    with pytest.raises(ValueError, match="id_cols"):
        param.validate()


def test_explain_parameter_validates_id_cols_is_set() -> None:
    """Test validation that id_cols is a set."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols=["not_a_set"],  # type: ignore[arg-type]
        depth=1,
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    with pytest.raises(ValueError, match="id_cols"):
        param.validate()


def test_explain_parameter_validates_depth_positive() -> None:
    """Test validation that depth is positive."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=0,  # Invalid: not positive
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    with pytest.raises(ValueError, match="depth"):
        param.validate()


def test_explain_parameter_validates_depth_negative() -> None:
    """Test validation that depth cannot be negative."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=-1,  # Invalid: negative
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    with pytest.raises(ValueError, match="depth"):
        param.validate()


def test_explain_parameter_validates_model_caslib() -> None:
    """Test validation that model_caslib is required."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        model_caslib="",  # Invalid: empty
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    with pytest.raises(ValueError, match="model_caslib"):
        param.validate()


def test_explain_parameter_validates_model_table() -> None:
    """Test validation that model_table is required."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        model_caslib="models",
        model_table="",  # Invalid: empty
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    with pytest.raises(ValueError, match="model_table"):
        param.validate()


def test_explain_parameter_validates_sas_score_code() -> None:
    """Test validation that sas_score_code is required."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        model_caslib="models",
        model_table="astore",
        sas_score_code="",  # Invalid: empty
        model_table_type=ModelTableType.ASTORE,
    )

    with pytest.raises(ValueError, match="sas_score_code"):
        param.validate()


def test_explain_parameter_successful_validation_astore() -> None:
    """Test successful validation with ASTORE model."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    param.validate()  # Should not raise


def test_explain_parameter_successful_validation_datastep() -> None:
    """Test successful validation with DataStep model."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        model_caslib="models",
        model_table="astore",
        sas_score_code="y = x1 * x2;",
        model_table_type=ModelTableType.DATASTEP,
    )

    param.validate()  # Should not raise


def test_explain_parameter_immutability() -> None:
    """Test that ExplainParameter instances are immutable."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    with pytest.raises(AttributeError):
        param.train_caslib = "other"  # type: ignore[misc]


def test_explain_parameter_equality() -> None:
    """Test equality comparison of ExplainParameter instances."""
    param1 = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1", "f2"],
        id_cols={"id"},
        depth=2,
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    param2 = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1", "f2"],
        id_cols={"id"},
        depth=2,
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    assert param1 == param2


def test_explain_parameter_inequality() -> None:
    """Test inequality comparison of ExplainParameter instances."""
    param1 = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    param2 = ExplainParameter(
        train_caslib="public",
        train_table="training_data_other",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    assert param1 != param2


def test_explain_parameter_multiple_id_cols() -> None:
    """Test ExplainParameter with multiple ID columns."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"customer_id", "transaction_id"},  # Multiple ID cols
        depth=2,
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    assert len(param.id_cols) == 2
    assert "customer_id" in param.id_cols
    assert "transaction_id" in param.id_cols


def test_explain_parameter_multiple_features() -> None:
    """Test ExplainParameter with many feature columns."""
    features = ["age", "income", "tenure", "credit_score", "balance", "products"]
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=features,
        id_cols={"id"},
        depth=3,
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
        model_table_type=ModelTableType.ASTORE,
    )

    assert param.features == features
    assert len(param.features) == 6
