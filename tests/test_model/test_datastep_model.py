"""Tests for DataStepModel concrete implementation."""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest
from typing_extensions import override

from sas_model_kit.model.concrete import DataStepModel
from sas_model_kit.model.executor import ModelExecutor
from sas_model_kit.model.payloads import DataStepPayload
from sas_model_kit.operation import OperationProtocol
from sas_model_kit.parameter import DataStepParameter


class FakeDataStepExecutor(ModelExecutor[DataStepParameter, DataStepPayload]):
    """Test double for DataStepExecutor."""

    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.call_count = 0

    @override
    def execute(
        self,
        operation: OperationProtocol,
        parameter: DataStepParameter,
        **context: Any,
    ) -> DataStepPayload:
        self.call_count += 1
        if self.should_fail:
            raise RuntimeError("Fake datastep failure")
        return DataStepPayload(
            success=True,
            message="DataStep executed successfully",
            output_caslib="public",
            output_table="processed_data",
        )


class TestDataStepModel:
    """Test DataStepModel concrete implementation."""

    def test_successful_execution(self) -> None:
        """Should execute and return Ok with DataStepPayload."""
        executor = FakeDataStepExecutor()
        model = DataStepModel(executor=executor)

        operation = Mock(spec=OperationProtocol)
        parameter = DataStepParameter(
            score_code="data public.result; run;",
            output_caslib="public",
            output_table="result",
        )

        result = model.execute(operation, parameter)

        assert result.is_ok
        success = result.unwrap()
        assert success.data.success is True
        assert "successfully" in success.data.message
        assert success.data.output_caslib == "public"
        assert success.data.output_table == "processed_data"
        assert success.metadata.rows_affected == 0
        assert executor.call_count == 1

    def test_failed_execution(self) -> None:
        """Should catch exception and return Err with ModelError."""
        executor = FakeDataStepExecutor(should_fail=True)
        model = DataStepModel(executor=executor)

        operation = Mock(spec=OperationProtocol)
        parameter = DataStepParameter(
            score_code="data work.test; run;",
            output_caslib="work",
            output_table="test",
        )

        result = model.execute(operation, parameter)

        assert result.is_err
        error = result.error
        assert "Fake datastep failure" in error.message
        assert isinstance(error.cause, RuntimeError)
        assert error.metadata.rows_affected == 0

    def test_immutable_model(self) -> None:
        """DataStepModel should be immutable (frozen)."""
        executor = FakeDataStepExecutor()
        model = DataStepModel(executor=executor)

        with pytest.raises(AttributeError):
            model.executor = FakeDataStepExecutor()  # type: ignore
