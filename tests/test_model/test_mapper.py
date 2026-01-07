"""Tests for parameter mappers."""

from __future__ import annotations

import pytest

from sas_model_kit.model.mapper.swat import (
    AstoreParameterToSwatDictMapper,
    DataStepParameterToSwatDictMapper,
    ExplainParameterToSwatDictMapper,
)
from sas_model_kit.parameter import (
    AstoreParameter,
    DataStepParameter,
    ExplainParameter,
)


class TestAstoreParameterToSwatDictMapper:
    """Test AstoreParameter to SWAT dict mapping."""

    def test_map_basic_astore(self) -> None:
        """Should map AstoreParameter to astore.score dict."""
        # Arrange
        param = AstoreParameter(
            input_caslib="public",
            input_table="customers",
            model_caslib="models",
            model_table="my_astore",
            score_code="dcl double x1-x5;",
        )
        mapper = AstoreParameterToSwatDictMapper()

        # Act
        result = mapper.map(param)

        # Assert
        assert result["table"] == {"name": "customers", "caslib": "public"}
        assert result["rstore"] == {"name": "my_astore", "caslib": "models"}
        assert result["out"]["caslib"] == "public"
        assert result["out"]["name"] == "customers_scored"
        assert result["code"] == "dcl double x1-x5;"

    def test_map_with_custom_casout(self) -> None:
        """Should use custom casout if provided."""
        # Arrange
        param = AstoreParameter(
            input_caslib="public",
            input_table="input",
            model_caslib="models",
            model_table="model",
            score_code="code",
            casout={"name": "custom_output", "caslib": "results", "promote": True},
        )
        mapper = AstoreParameterToSwatDictMapper()

        # Act
        result = mapper.map(param)

        # Assert
        assert result["out"]["name"] == "custom_output"
        assert result["out"]["caslib"] == "results"
        assert result["out"]["promote"] is True

    def test_map_with_context_override(self) -> None:
        """Should use context to override output location."""
        # Arrange
        param = AstoreParameter(
            input_caslib="public",
            input_table="input",
            model_caslib="models",
            model_table="model",
            score_code="code",
        )
        mapper = AstoreParameterToSwatDictMapper()

        # Act
        result = mapper.map(
            param, output_caslib="custom_lib", output_table="custom_table"
        )

        # Assert
        assert result["out"]["caslib"] == "custom_lib"
        assert result["out"]["name"] == "custom_table"

    def test_map_invalid_parameter(self) -> None:
        """Should raise ValueError for invalid parameter."""
        # Arrange
        param = AstoreParameter(
            input_caslib="",  # Invalid: empty
            input_table="input",
            model_caslib="models",
            model_table="model",
            score_code="code",
        )
        mapper = AstoreParameterToSwatDictMapper()

        # Act & Assert
        with pytest.raises(ValueError, match="input_caslib"):
            mapper.map(param)


class TestExplainParameterToSwatDictMapper:
    """Test ExplainParameter to SWAT dict mapping."""

    def test_map_astore_model(self) -> None:
        """Should map ExplainParameter with ASTORE model."""
        # Arrange
        param = ExplainParameter(
            train_caslib="public",
            train_table="training",
            predicted_target="churn",
            features=["age", "income"],
            id_cols={"customer_id"},
            depth=1,
            model_caslib="models",
            model_table="astore_model",
        )
        mapper = ExplainParameterToSwatDictMapper()

        # Act
        result = mapper.map(param, where_condition="customer_id=123")

        # Assert
        assert result["modelTableType"] == "ASTORE"
        assert result["id"] == "customer_id"
        assert result["depth"] == 1
        assert result["trainTable"] == {"name": "training", "caslib": "public"}
        assert result["target"] == "churn"
        assert "age" in result["inputs"]
        assert "income" in result["inputs"]
        assert result["modelTable"] == {
            "name": "astore_model",
            "caslib": "models",
        }
        assert result["where"] == "customer_id=123"

    def test_map_datastep_model(self) -> None:
        """Should map ExplainParameter with DataStep model."""
        # Arrange
        param = ExplainParameter(
            train_caslib="public",
            train_table="training",
            predicted_target="target",
            features=["f1", "f2"],
            id_cols={"id"},
            depth=2,
            sas_score_code="y = a*x1 + b*x2;",
        )
        mapper = ExplainParameterToSwatDictMapper()

        # Act
        result = mapper.map(param)

        # Assert
        assert result["modelTableType"] == "DATASTEP"
        assert result["code"] == "y = a*x1 + b*x2;"
        assert "modelTable" not in result

    def test_map_with_multiple_id_cols(self) -> None:
        """Should handle multiple ID columns."""
        # Arrange
        param = ExplainParameter(
            train_caslib="public",
            train_table="training",
            predicted_target="target",
            features=["f1"],
            id_cols={"id1", "id2", "id3"},
            depth=1,
            model_caslib="models",
            model_table="model",
        )
        mapper = ExplainParameterToSwatDictMapper()

        # Act
        result = mapper.map(param)

        # Assert
        id_str = result["id"]
        assert "id1" in id_str
        assert "id2" in id_str
        assert "id3" in id_str

    def test_map_with_score_data(self) -> None:
        """Should include score data if provided."""
        # Arrange
        param = ExplainParameter(
            train_caslib="public",
            train_table="training",
            predicted_target="target",
            features=["f1"],
            id_cols={"id"},
            depth=1,
            model_caslib="models",
            model_table="model",
            score_caslib="public",
            score_table="test_data",
        )
        mapper = ExplainParameterToSwatDictMapper()

        # Act
        result = mapper.map(param)

        # Assert
        assert result["scoreTable"] == {"name": "test_data", "caslib": "public"}

    def test_map_no_model_raises_error(self) -> None:
        """Should raise ValueError if no model specified."""
        # Arrange
        param = ExplainParameter(
            train_caslib="public",
            train_table="training",
            predicted_target="target",
            features=["f1"],
            id_cols={"id"},
            depth=1,
            # No model_caslib/model_table or sas_score_code
        )
        mapper = ExplainParameterToSwatDictMapper()

        # Act & Assert
        with pytest.raises(ValueError, match="model"):
            mapper.map(param)


class TestDataStepParameterToSwatDictMapper:
    """Test DataStepParameter to SWAT dict mapping."""

    def test_map_basic_datastep(self) -> None:
        """Should map DataStepParameter to datastep.runCode dict."""
        # Arrange
        code = """
            data public.result;
            set public.input;
            x = a + b;
            run;
        """
        param = DataStepParameter(score_code=code)
        mapper = DataStepParameterToSwatDictMapper()

        # Act
        result = mapper.map(param)

        # Assert
        assert result["code"] == code
        assert result["single"] is True

    def test_map_with_casout(self) -> None:
        """Should include casout if provided."""
        # Arrange
        param = DataStepParameter(
            score_code="data x; run;",
            casout={"name": "output", "caslib": "public"},
        )
        mapper = DataStepParameterToSwatDictMapper()

        # Act
        result = mapper.map(param)

        # Assert
        assert result["casout"] == {"name": "output", "caslib": "public"}

    def test_map_invalid_parameter(self) -> None:
        """Should raise ValueError for empty code."""
        # Arrange
        param = DataStepParameter(score_code="")  # Invalid: empty
        mapper = DataStepParameterToSwatDictMapper()

        # Act & Assert
        with pytest.raises(ValueError, match="score_code"):
            mapper.map(param)
