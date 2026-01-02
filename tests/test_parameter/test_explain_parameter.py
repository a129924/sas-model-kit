"""Tests for ExplainParameter class."""

from __future__ import annotations

import pytest

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
    )

    assert param.train_caslib == "public"
    assert param.train_table == "training_data"
    assert param.predicted_target == "churn_pred"
    assert param.features == ["age", "income", "tenure"]
    assert param.id_cols == {"customer_id"}
    assert param.depth == 2
    assert param.model_caslib == "models"
    assert param.model_table == "my_astore"
    assert param.score_caslib is None
    assert param.score_table is None
    assert param.sas_score_code is None
    assert param.casout is None


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
    )

    assert param.sas_score_code == sas_code
    assert param.model_caslib is None
    assert param.model_table is None


def test_explain_parameter_with_score_data() -> None:
    """Test ExplainParameter with optional score data."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        score_caslib="public",
        score_table="test_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=2,
        model_caslib="models",
        model_table="astore",
    )

    assert param.score_caslib == "public"
    assert param.score_table == "test_data"


def test_explain_parameter_with_casout() -> None:
    """Test ExplainParameter with custom casout."""
    casout = {"name": "explain_results", "promote": True}
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        model_caslib="models",
        model_table="astore",
        casout=casout,
    )

    assert param.casout == casout


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
    )

    with pytest.raises(ValueError, match="train_caslib cannot be empty"):
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
    )

    with pytest.raises(ValueError, match="train_table cannot be empty"):
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
    )

    with pytest.raises(ValueError, match="predicted_target cannot be empty"):
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
    )

    with pytest.raises(ValueError, match="features must be a non-empty list"):
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
    )

    with pytest.raises(ValueError, match="features must be a non-empty list"):
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
    )

    with pytest.raises(ValueError, match="id_cols must be a non-empty set"):
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
    )

    with pytest.raises(ValueError, match="id_cols must be a non-empty set"):
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
    )

    with pytest.raises(ValueError, match="depth must be a positive integer"):
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
    )

    with pytest.raises(ValueError, match="depth must be a positive integer"):
        param.validate()


def test_explain_parameter_validates_score_caslib_and_table_paired() -> None:
    """Test validation that score_caslib and score_table must be paired."""
    # Only score_caslib, missing score_table
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        score_caslib="public",  # Missing score_table
        score_table=None,
        model_caslib="models",
        model_table="astore",
    )

    with pytest.raises(
        ValueError, match="score_caslib and score_table must both be provided"
    ):
        param.validate()


def test_explain_parameter_validates_model_caslib_and_table_paired() -> None:
    """Test validation that model_caslib and model_table must be paired."""
    # Only model_caslib, missing model_table
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        model_caslib="models",
        model_table="",  # Invalid: empty
        sas_score_code=None,  # No DataStep model
    )

    with pytest.raises(
        ValueError, match="model_caslib and model_table must both be provided"
    ):
        param.validate()


def test_explain_parameter_validates_at_least_one_model() -> None:
    """Test validation that at least one model must be provided."""
    # Neither ASTORE nor DataStep
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        model_caslib=None,
        model_table=None,
        sas_score_code=None,
    )

    with pytest.raises(ValueError, match="At least one model must be provided"):
        param.validate()


def test_explain_parameter_validates_casout_dict() -> None:
    """Test validation that casout is a dict."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        model_caslib="models",
        model_table="astore",
        casout="not_a_dict",  # type: ignore[arg-type]
    )

    with pytest.raises(ValueError, match="casout must be a dictionary or None"):
        param.validate()


def test_explain_parameter_validates_casout_has_name() -> None:
    """Test validation that casout['name'] is required."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        model_caslib="models",
        model_table="astore",
        casout={"promote": True},  # Missing 'name'
    )

    with pytest.raises(ValueError, match="casout\\['name'\\]"):
        param.validate()


def test_explain_parameter_successful_validation_minimal() -> None:
    """Test successful validation with minimal fields."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        model_caslib="models",
        model_table="astore",
    )

    # Should not raise
    param.validate()


def test_explain_parameter_successful_validation_with_all_fields() -> None:
    """Test successful validation with all optional fields."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        score_caslib="public",
        score_table="test_data",
        predicted_target="target",
        features=["f1", "f2", "f3"],
        id_cols={"customer_id", "transaction_id"},
        depth=3,
        model_caslib="models",
        model_table="astore",
        sas_score_code="new_var = var1 * 2;",
        casout={"name": "explain_output", "promote": True},
    )

    # Should not raise
    param.validate()


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
    )

    with pytest.raises(AttributeError):
        param.depth = 5  # type: ignore[misc]


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
    )
    param3 = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1", "f2"],
        id_cols={"id"},
        depth=3,  # Different
        model_caslib="models",
        model_table="astore",
    )

    assert param1 == param2
    assert param1 != param3


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
    )

    assert param.id_cols == {"customer_id", "transaction_id"}
    param.validate()  # Should not raise


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
    )

    assert param.features == features
    assert len(param.features) == 6
    param.validate()  # Should not raise


def test_explain_parameter_only_datastep_model() -> None:
    """Test ExplainParameter with only DataStep model (no ASTORE)."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        sas_score_code="new_var = var1 * var2;",
    )

    assert param.sas_score_code is not None
    assert param.model_caslib is None
    assert param.model_table is None
    param.validate()  # Should not raise


def test_explain_parameter_with_score_data_only() -> None:
    """Test ExplainParameter with score data (no ASTORE, only code)."""
    param = ExplainParameter(
        train_caslib="public",
        train_table="training_data",
        score_caslib="public",
        score_table="test_data",
        predicted_target="target",
        features=["f1"],
        id_cols={"id"},
        depth=1,
        sas_score_code="new_var = var1 * 2;",
    )

    assert param.score_caslib == "public"
    assert param.score_table == "test_data"
    param.validate()  # Should not raise
