"""Tests for ShapleyValuesTransformer."""

import pytest
from swat.dataframe import SASDataFrame

from sas_model_kit.transformer.shapley_values import ShapleyValuesTransformer


def test_shapley_transform_basic() -> None:
    """Transforms long to wide and appends id column."""
    # Simulate SASDataFrame with pandas
    df = SASDataFrame(
        {
            "Variable": ["age", "income", "region"],
            "ShapleyValue": [0.12, -0.03, 0.55],
        }
    )

    t = ShapleyValuesTransformer(id_column="_id")
    wide = t.transform(df, id_value="u123")

    # Expect one row, columns: age, income, region, _id
    assert wide.shape[0] == 1
    for col in ["age", "income", "region", "_id"]:
        assert col in wide.columns
    assert wide.loc[:, "_id"].iloc[0] == "u123"


def test_shapley_transform_missing_columns_raises() -> None:
    """Missing required columns should raise ValueError."""
    df = SASDataFrame({"foo": [1, 2], "bar": [3, 4]})
    t = ShapleyValuesTransformer(id_column="_id")

    with pytest.raises(KeyError):
        _ = t.transform(df, id_value=1)


def test_shapley_transform_preserves_values() -> None:
    """Values for variables are preserved after transposition."""
    df = SASDataFrame(
        {
            "Variable": ["v1", "v2"],
            "ShapleyValue": [0.1, 0.2],
        }
    )
    t = ShapleyValuesTransformer(id_column="_id")
    wide = t.transform(df, id_value="abc")

    assert pytest.approx(wide.loc[:, "v1"].iloc[0], 0.0001) == 0.1
    assert pytest.approx(wide.loc[:, "v2"].iloc[0], 0.0001) == 0.2
