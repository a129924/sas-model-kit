"""Tests for Model payload types."""

from __future__ import annotations

import pytest

from sas_model_kit.model.payloads import (
    AstorePayload,
    DataStepPayload,
    ExplainPayload,
)


class TestAstorePayload:
    """Test AstorePayload dataclass."""

    def test_creation_minimal(self) -> None:
        """Test creating AstorePayload with minimal fields."""
        payload = AstorePayload(
            output_caslib="public",
            output_table="scored_data",
            rows_scored=1000,
        )

        assert payload.output_caslib == "public"
        assert payload.output_table == "scored_data"
        assert payload.rows_scored == 1000
        assert payload.cas_table is None

    def test_creation_with_cas_table(self) -> None:
        """Test creating AstorePayload with CASTable reference."""
        # Mock CASTable for testing
        mock_table = object()

        payload = AstorePayload(
            output_caslib="public",
            output_table="scored_data",
            rows_scored=500,
            cas_table=mock_table,  # type: ignore
        )

        assert payload.cas_table is mock_table

    def test_immutability(self) -> None:
        """Test that AstorePayload is immutable."""
        payload = AstorePayload(
            output_caslib="public",
            output_table="data",
            rows_scored=100,
        )

        with pytest.raises(AttributeError):
            payload.output_caslib = "new_lib"  # type: ignore

    def test_equality(self) -> None:
        """Test payload equality comparison."""
        payload1 = AstorePayload(
            output_caslib="public",
            output_table="data",
            rows_scored=100,
        )
        payload2 = AstorePayload(
            output_caslib="public",
            output_table="data",
            rows_scored=100,
        )
        payload3 = AstorePayload(
            output_caslib="public",
            output_table="data",
            rows_scored=200,  # Different
        )

        assert payload1 == payload2
        assert payload1 != payload3


class TestExplainPayload:
    """Test ExplainPayload dataclass."""

    def test_creation_minimal(self) -> None:
        """Test creating ExplainPayload with minimal fields."""
        shapley_data = [
            {"Variable": "age", "ShapleyValue": 0.15},
            {"Variable": "income", "ShapleyValue": 0.32},
        ]

        payload = ExplainPayload(shapley_values=shapley_data)

        assert payload.shapley_values == shapley_data
        assert payload.output_caslib is None
        assert payload.output_table is None

    def test_creation_with_output_location(self) -> None:
        """Test creating ExplainPayload with output location."""
        shapley_data = [{"Variable": "x", "ShapleyValue": 0.5}]

        payload = ExplainPayload(
            shapley_values=shapley_data,
            output_caslib="explain_lib",
            output_table="results_123",
        )

        assert payload.output_caslib == "explain_lib"
        assert payload.output_table == "results_123"

    def test_empty_shapley_values(self) -> None:
        """Test payload with empty Shapley values list."""
        payload = ExplainPayload(shapley_values=[])

        assert payload.shapley_values == []
        assert len(payload.shapley_values) == 0

    def test_immutability(self) -> None:
        """Test that ExplainPayload is immutable."""
        payload = ExplainPayload(
            shapley_values=[{"Variable": "x", "ShapleyValue": 1.0}]
        )

        with pytest.raises(AttributeError):
            payload.output_caslib = "new_lib"  # type: ignore


class TestDataStepPayload:
    """Test DataStepPayload dataclass."""

    def test_creation_success(self) -> None:
        """Test creating DataStepPayload for successful execution."""
        payload = DataStepPayload(
            success=True,
            message="DataStep executed successfully",
            output_caslib="public",
            output_table="processed_data",
        )

        assert payload.success is True
        assert payload.message == "DataStep executed successfully"
        assert payload.output_caslib == "public"
        assert payload.output_table == "processed_data"

    def test_creation_failure(self) -> None:
        """Test creating DataStepPayload for failed execution."""
        payload = DataStepPayload(
            success=False,
            message="Syntax error in DATA step",
            output_caslib="",
            output_table="",
        )

        assert payload.success is False
        assert "error" in payload.message.lower()

    def test_detailed_message(self) -> None:
        """Test payload with detailed execution message."""
        payload = DataStepPayload(
            success=True,
            message="Processed 10000 rows, created 3 new variables",
            output_caslib="work",
            output_table="temp_result",
        )

        assert "10000 rows" in payload.message
        assert "3 new variables" in payload.message

    def test_immutability(self) -> None:
        """Test that DataStepPayload is immutable."""
        payload = DataStepPayload(
            success=True,
            message="OK",
            output_caslib="public",
            output_table="data",
        )

        with pytest.raises(AttributeError):
            payload.success = False  # type: ignore


class TestPayloadIntegration:
    """Test payload types work together in workflows."""

    def test_astore_to_explain_workflow(self) -> None:
        """Test payloads can be chained in Astore → Explain workflow."""
        # Step 1: Astore scoring
        astore_payload = AstorePayload(
            output_caslib="public",
            output_table="scored_customers",
            rows_scored=5000,
        )

        # Step 2: Use Astore output for Explain
        # (In real code, these would be passed to ExplainParameter)
        input_caslib = astore_payload.output_caslib
        input_table = astore_payload.output_table

        assert input_caslib == "public"
        assert input_table == "scored_customers"

        # Step 3: Explain execution
        explain_payload = ExplainPayload(
            shapley_values=[{"Variable": "age", "ShapleyValue": 0.2}],
            output_caslib="explain_results",
            output_table="customer_explain",
        )

        assert len(explain_payload.shapley_values) == 1

    def test_datastep_to_model_workflow(self) -> None:
        """Test DataStep preprocessing output can be used for model input."""
        # Step 1: DataStep preprocessing
        datastep_payload = DataStepPayload(
            success=True,
            message="Preprocessing complete",
            output_caslib="work",
            output_table="preprocessed",
        )

        assert datastep_payload.success

        # Step 2: Use DataStep output as model input
        model_input_caslib = datastep_payload.output_caslib
        model_input_table = datastep_payload.output_table

        assert model_input_caslib == "work"
        assert model_input_table == "preprocessed"
