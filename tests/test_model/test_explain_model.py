"""Tests for ExplainModel concrete implementation."""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest
from typing_extensions import override

from sas_model_kit.model.concrete import ExplainModel
from sas_model_kit.model.executor import ModelExecutor
from sas_model_kit.model.payloads import ExplainPayload
from sas_model_kit.model.types import ModelTableType
from sas_model_kit.operation import OperationProtocol
from sas_model_kit.parameter import ExplainParameter


class FakeExplainExecutor(ModelExecutor[ExplainParameter, ExplainPayload]):
    """Test double for ExplainExecutor."""

    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.call_count = 0

    @override
    def execute(
        self,
        operation: OperationProtocol,
        parameter: ExplainParameter,
        **context: Any,
    ) -> ExplainPayload:
        self.call_count += 1
        if self.should_fail:
            raise RuntimeError("Fake executor failure")
        return ExplainPayload(
            shapley_values=[
                {"Variable": "age", "ShapleyValue": 0.42},
                {"Variable": "income", "ShapleyValue": 0.28},
            ],
            output_caslib="test_lib",
            output_table="test_table",
        )


class TestExplainModel:
    """Test ExplainModel concrete implementation."""

    def test_successful_execution(self) -> None:
        """Should execute and return Ok with ExplainPayload."""
        executor = FakeExplainExecutor()
        model = ExplainModel(executor=executor)

        operation = Mock(spec=OperationProtocol)
        parameter = ExplainParameter(
            train_caslib="public",
            train_table="training",
            predicted_target="target",
            features=["age", "income"],
            id_cols={"customer_id"},
            depth=1,
            model_table_type=ModelTableType.ASTORE,
            model_caslib="models",
            model_table="astore",
            sas_score_code="code",
        )

        result = model.execute(operation, parameter, where_condition="id='123'")

        assert result.is_ok
        assert not result.is_err
        success = result.unwrap()
        assert success.data.shapley_values == [
            {"Variable": "age", "ShapleyValue": 0.42},
            {"Variable": "income", "ShapleyValue": 0.28},
        ]
        assert success.metadata.rows_affected == 2
        assert executor.call_count == 1

    def test_failed_execution(self) -> None:
        """Should catch exception and return Err with ModelError."""
        executor = FakeExplainExecutor(should_fail=True)
        model = ExplainModel(executor=executor)

        operation = Mock(spec=OperationProtocol)
        parameter = ExplainParameter(
            train_caslib="public",
            train_table="training",
            predicted_target="target",
            features=["age"],
            id_cols={"id"},
            depth=1,
            model_table_type=ModelTableType.ASTORE,
            model_caslib="models",
            model_table="model",
            sas_score_code="code",
        )

        result = model.execute(operation, parameter)

        assert result.is_err
        assert not result.is_ok
        error = result.error
        assert "Fake executor failure" in error.message
        assert error.cause is not None
        assert isinstance(error.cause, RuntimeError)
        assert error.metadata.rows_affected == 0

    def test_context_passed_to_executor(self) -> None:
        """Should pass context to executor."""

        class TrackingExecutor(FakeExplainExecutor):
            def __init__(self) -> None:
                super().__init__()
                self.received_context: dict[str, Any] = {}

            @override
            def execute(
                self,
                operation: OperationProtocol,
                parameter: ExplainParameter,
                **context: Any,
            ) -> ExplainPayload:
                self.received_context = context
                return super().execute(operation, parameter, **context)

        executor = TrackingExecutor()
        model = ExplainModel(executor=executor)

        operation = Mock(spec=OperationProtocol)
        parameter = ExplainParameter(
            train_caslib="public",
            train_table="train",
            predicted_target="target",
            features=["x"],
            id_cols={"id"},
            depth=1,
            model_table_type=ModelTableType.ASTORE,
            model_caslib="models",
            model_table="model",
            sas_score_code="code",
        )

        model.execute(
            operation,
            parameter,
            where_condition="id='999'",
            output_caslib="custom_lib",
        )

        assert executor.received_context["where_condition"] == "id='999'"
        assert executor.received_context["output_caslib"] == "custom_lib"

    def test_immutable_model(self) -> None:
        """ExplainModel should be immutable (frozen)."""
        executor = FakeExplainExecutor()
        model = ExplainModel(executor=executor)

        with pytest.raises(AttributeError):
            model.executor = FakeExplainExecutor()  # type: ignore
