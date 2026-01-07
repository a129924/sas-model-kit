"""Tests for AstoreModel concrete implementation."""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest
from typing_extensions import override

from sas_model_kit.model.concrete import AstoreModel
from sas_model_kit.model.executor import ModelExecutor
from sas_model_kit.model.payloads import AstorePayload
from sas_model_kit.operation import OperationProtocol
from sas_model_kit.parameter import AstoreParameter


class FakeAstoreExecutor(ModelExecutor[AstoreParameter, AstorePayload]):
    """Test double for AstoreExecutor."""

    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.call_count = 0

    @override
    def execute(
        self,
        operation: OperationProtocol,
        parameter: AstoreParameter,
        **context: Any,
    ) -> AstorePayload:
        self.call_count += 1
        if self.should_fail:
            raise RuntimeError("Fake astore failure")
        return AstorePayload(
            output_caslib="public",
            output_table="scored_data",
            rows_scored=1000,
            cas_table=None,
        )


class TestAstoreModel:
    """Test AstoreModel concrete implementation."""

    def test_successful_execution(self) -> None:
        """Should execute and return Ok with AstorePayload."""
        executor = FakeAstoreExecutor()
        model = AstoreModel(executor=executor)

        operation = Mock(spec=OperationProtocol)
        parameter = AstoreParameter(
            input_caslib="public",
            input_table="customers",
            model_caslib="models",
            model_table="my_astore",
            score_code="dcl double x;",
        )

        result = model.execute(operation, parameter)

        assert result.is_ok
        success = result.unwrap()
        assert success.data.output_caslib == "public"
        assert success.data.output_table == "scored_data"
        assert success.data.rows_scored == 1000
        assert success.metadata.rows_affected == 1000
        assert executor.call_count == 1

    def test_failed_execution(self) -> None:
        """Should catch exception and return Err with ModelError."""
        executor = FakeAstoreExecutor(should_fail=True)
        model = AstoreModel(executor=executor)

        operation = Mock(spec=OperationProtocol)
        parameter = AstoreParameter(
            input_caslib="public",
            input_table="input",
            model_caslib="models",
            model_table="model",
            score_code="code",
        )

        result = model.execute(operation, parameter)

        assert result.is_err
        error = result.error
        assert "Fake astore failure" in error.message
        assert isinstance(error.cause, RuntimeError)
        assert error.metadata.rows_affected == 0

    def test_immutable_model(self) -> None:
        """AstoreModel should be immutable (frozen)."""
        executor = FakeAstoreExecutor()
        model = AstoreModel(executor=executor)

        with pytest.raises(AttributeError):
            model.executor = FakeAstoreExecutor()  # type: ignore
