"""Tests for SyncModel abstract base class."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from sas_model_kit.model import SyncModel
from sas_model_kit.operation import OperationProtocol
from sas_model_kit.parameter import BaseModelParameter
from sas_model_kit.result import ModelResult, ResultStatus


class ConcreteModel(SyncModel):
    """Concrete implementation for testing."""

    def execute(
        self,
        operation: OperationProtocol,
        parameter: BaseModelParameter,
    ) -> ModelResult:
        """Simple implementation returning success."""
        return ModelResult(
            status=ResultStatus.SUCCESS,
            data={"result": "success"},
        )


class FailingModel(SyncModel):
    """Model that always fails for testing error cases."""

    def execute(
        self,
        operation: OperationProtocol,
        parameter: BaseModelParameter,
    ) -> ModelResult:
        """Implementation that returns error."""
        return ModelResult(
            status=ResultStatus.ERROR,
            data=None,
            metadata={"error": "Model execution failed"},
        )


def test_sync_model_is_abstract() -> None:
    """Test that SyncModel cannot be instantiated directly."""
    # Should raise TypeError when trying to instantiate abstract class
    with pytest.raises(TypeError):
        SyncModel()  # type: ignore[abstract]


def test_sync_model_concrete_implementation() -> None:
    """Test creating concrete SyncModel implementation."""
    model = ConcreteModel()
    assert isinstance(model, SyncModel)


def test_sync_model_execute_returns_result() -> None:
    """Test that execute method returns ModelResult."""
    model = ConcreteModel()
    operation = MagicMock(spec=OperationProtocol)
    parameter = MagicMock(spec=BaseModelParameter)

    result = model.execute(operation, parameter)

    assert isinstance(result, ModelResult)
    assert result.is_success


def test_sync_model_execute_with_error() -> None:
    """Test execute method returning error result."""
    model = FailingModel()
    operation = MagicMock(spec=OperationProtocol)
    parameter = MagicMock(spec=BaseModelParameter)

    result = model.execute(operation, parameter)

    assert isinstance(result, ModelResult)
    assert result.is_error
    assert result.metadata["error"] == "Model execution failed"


def test_sync_model_execute_signature() -> None:
    """Test that execute method has correct signature."""
    model = ConcreteModel()

    # Check method exists
    assert hasattr(model, "execute")
    assert callable(model.execute)

    # Check method signature through annotations
    execute_method = model.execute
    assert hasattr(execute_method, "__annotations__")
    annotations = execute_method.__annotations__

    # Verify parameter types are documented
    assert "operation" in annotations
    assert "parameter" in annotations
    assert "return" in annotations


def test_sync_model_subclass_must_implement_execute() -> None:
    """Test that subclass must implement execute method."""

    with pytest.raises(TypeError):
        # Missing execute implementation
        class IncompleteModel(SyncModel):  # type: ignore[misc]
            pass

        IncompleteModel()


def test_sync_model_accepts_operation_protocol() -> None:
    """Test that model accepts OperationProtocol implementation."""
    model = ConcreteModel()
    operation = MagicMock(spec=OperationProtocol)
    parameter = MagicMock(spec=BaseModelParameter)

    # Should not raise
    result = model.execute(operation, parameter)
    assert result is not None
