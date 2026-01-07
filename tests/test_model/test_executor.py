"""Tests for SWAT executors."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from typing_extensions import override

from sas_model_kit.model.executor import (
    SwatAstoreExecutor,
    SwatDataStepExecutor,
    SwatExplainExecutor,
)
from sas_model_kit.model.types import ModelTableType
from sas_model_kit.operation import OperationProtocol
from sas_model_kit.parameter import AstoreParameter, DataStepParameter, ExplainParameter


class FakeOperation(OperationProtocol[Any]):
    """Test double for OperationProtocol that records action calls."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    @override
    def call_action(self, action_name: str, **kwargs: Any) -> Any:
        self.calls.append((action_name, kwargs))
        if action_name == "astore.score":
            return {"ScoreInfo": [{"NObs": 12}]}
        if action_name == "explainModel.shapleyExplainer":
            # Mock SASDataFrame from SWAT
            mock_df = MagicMock()
            mock_df.empty = False
            mock_df.to_dict.return_value = [{"Variable": "age", "ShapleyValue": 0.42}]
            return {"ShapleyValues": mock_df}
        if action_name == "datastep.runCode":
            return {"status": False, "reason": "syntax error"}
        return {}

    @override
    def upload_data(self, data: Any, caslib: str, table: str) -> None:
        return None

    @override
    def table_exists(self, caslib: str, table: str) -> bool:
        return True

    @override
    def model_exists(self, caslib: str, table: str) -> bool:
        return True


class TestSwatAstoreExecutor:
    """Tests for SwatAstoreExecutor."""

    def test_execute_returns_payload(self) -> None:
        operation = FakeOperation()
        parameter = AstoreParameter(
            input_caslib="public",
            input_table="customers",
            model_caslib="models",
            model_table="astore_model",
            score_code="dcl double x;",
        )
        executor = SwatAstoreExecutor()

        payload = executor.execute(operation, parameter)

        assert payload.output_caslib == "public"
        assert payload.output_table == "customers_scored"
        assert payload.rows_scored == 12
        assert len(operation.calls) == 1
        action_name, action_kwargs = operation.calls[0]
        assert action_name == "astore.score"
        assert action_kwargs["table"] == {"name": "customers", "caslib": "public"}


class TestSwatExplainExecutor:
    """Tests for SwatExplainExecutor."""

    def test_execute_returns_shapley_payload(self) -> None:
        operation = FakeOperation()
        parameter = ExplainParameter(
            train_caslib="public",
            train_table="training",
            predicted_target="target",
            features=["age", "income"],
            id_cols={"customer_id"},
            depth=1,
            model_table_type=ModelTableType.ASTORE,
            model_caslib="models",
            model_table="astore_model",
            sas_score_code="score code",
        )
        executor = SwatExplainExecutor()

        payload = executor.execute(
            operation,
            parameter,
            where_condition="customer_id=1",
            output_caslib="work",
            output_table="shapley_out",
        )

        assert len(payload.shapley_values) == 1
        assert payload.shapley_values[0]["Variable"] == "age"
        assert payload.output_caslib == "work"
        assert payload.output_table == "shapley_out"
        assert operation.calls[0][0] == "explainModel.shapleyExplainer"


class TestSwatDataStepExecutor:
    """Tests for SwatDataStepExecutor."""

    def test_execute_returns_status_payload(self) -> None:
        operation = FakeOperation()
        parameter = DataStepParameter(
            score_code="data work.out; run;",
            output_caslib="public",
            output_table="processed",
        )
        executor = SwatDataStepExecutor()

        payload = executor.execute(operation, parameter)

        assert payload.success is False
        assert "syntax" in payload.message
        assert payload.output_caslib == "public"
        assert payload.output_table == "processed"
        assert operation.calls[0][0] == "datastep.runCode"
