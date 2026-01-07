"""Tests for SyncModel base class."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from typing_extensions import override

from sas_model_kit.model.sync_model import SyncModel
from sas_model_kit.operation import OperationProtocol
from sas_model_kit.parameter import BaseModelParameter
from sas_model_kit.result import Err, ModelError, ModelSuccess, Ok, Result


class TestSyncModelABC:
    """Test SyncModel as an abstract base class."""

    def test_cannot_instantiate_sync_model_directly(self) -> None:
        """Should not be able to instantiate SyncModel directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            SyncModel()  # type: ignore

    def test_must_implement_execute(self) -> None:
        """Concrete implementations must implement execute()."""

        @dataclass(frozen=True)
        class IncompleteModel(SyncModel[BaseModelParameter, Any]):
            pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteModel()  # type: ignore


class TestSyncModelConcrete:
    """Test concrete SyncModel implementation."""

    def test_concrete_implementation_works(self) -> None:
        """Can create concrete implementation with execute()."""

        @dataclass(frozen=True)
        class ConcreteModel(SyncModel[BaseModelParameter, dict[str, Any]]):
            test_value: str = "test"

            @override
            def execute(
                self,
                operation: OperationProtocol,
                parameter: BaseModelParameter,
                **context: Any,
            ) -> Result[ModelSuccess[dict[str, Any]], ModelError]:
                return Ok(
                    ModelSuccess(
                        data={"test": self.test_value},
                        metadata={"execution_mode": "test"},
                    )
                )

        model = ConcreteModel(test_value="hello")
        assert model.test_value == "hello"

    def test_execute_returns_result_type(self) -> None:
        """execute() should return Result[ModelSuccess, ModelError]."""

        @dataclass(frozen=True)
        class TestModel(SyncModel[BaseModelParameter, str]):
            @override
            def execute(
                self,
                operation: OperationProtocol,
                parameter: BaseModelParameter,
                **context: Any,
            ) -> Result[ModelSuccess[str], ModelError]:
                return Ok(ModelSuccess(data="success", metadata={}))

        # Create mock operation and parameter
        operation = object()  # type: ignore
        parameter = object()  # type: ignore

        model = TestModel()
        result = model.execute(operation, parameter)

        assert result.is_ok
        assert not result.is_err
        assert result.unwrap().data == "success"

    def test_frozen_dataclass(self) -> None:
        """SyncModel should be frozen (immutable)."""

        @dataclass(frozen=True)
        class FrozenModel(SyncModel[BaseModelParameter, str]):
            value: str = "test"

            @override
            def execute(
                self,
                operation: OperationProtocol,
                parameter: BaseModelParameter,
                **context: Any,
            ) -> Result[ModelSuccess[str], ModelError]:
                return Ok(ModelSuccess(data=self.value, metadata={}))

        model = FrozenModel(value="original")
        with pytest.raises(AttributeError):
            model.value = "modified"  # type: ignore


class TestSyncModelGeneric:
    """Test SyncModel generic type parameters."""

    def test_generic_parameter_type(self) -> None:
        """Can specify different parameter types."""

        class CustomParameter(BaseModelParameter):
            def validate(self) -> None:
                pass

        @dataclass(frozen=True)
        class GenericModel(SyncModel[CustomParameter, str]):
            @override
            def execute(
                self,
                operation: OperationProtocol,
                parameter: CustomParameter,
                **context: Any,
            ) -> Result[ModelSuccess[str], ModelError]:
                return Ok(ModelSuccess(data="custom", metadata={}))

        model = GenericModel()
        assert model is not None

    def test_generic_payload_type(self) -> None:
        """Can specify different payload types."""

        @dataclass
        class CustomPayload:
            value: int

        @dataclass(frozen=True)
        class PayloadModel(SyncModel[BaseModelParameter, CustomPayload]):
            @override
            def execute(
                self,
                operation: OperationProtocol,
                parameter: BaseModelParameter,
                **context: Any,
            ) -> Result[ModelSuccess[CustomPayload], ModelError]:
                payload = CustomPayload(value=42)
                return Ok(ModelSuccess(data=payload, metadata={}))

        model = PayloadModel()
        operation = object()  # type: ignore
        parameter = object()  # type: ignore

        result = model.execute(operation, parameter)
        assert result.is_ok
        assert result.unwrap().data.value == 42
