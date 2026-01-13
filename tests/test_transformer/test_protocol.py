"""Tests for CASTableTransformer protocol."""

from unittest.mock import Mock

import pytest

from sas_model_kit.transformer.protocol import CASTableTransformer
from sas_model_kit.result import Ok


def test_transformer_protocol_is_abstract() -> None:
    """Test that CASTableTransformer cannot be instantiated directly."""
    mock_operation = Mock()

    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        CASTableTransformer(mock_operation)  # type: ignore[abstract]


def test_transformer_requires_execute_implementation() -> None:
    """Test that subclass must implement execute method."""

    class BadTransformer(CASTableTransformer):
        pass  # Missing execute() implementation

    mock_operation = Mock()

    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BadTransformer(mock_operation)  # type: ignore[abstract]


def test_transformer_with_execute_implementation() -> None:
    """Test that subclass with execute() can be instantiated."""

    class GoodTransformer(CASTableTransformer):
        def execute(self, input_table):
            return Ok(input_table)

    mock_operation = Mock()
    transformer = GoodTransformer(mock_operation)

    assert transformer.operation == mock_operation
    assert hasattr(transformer, "execute")


def test_transformer_stores_operation() -> None:
    """Test that transformer stores the operation instance."""
    mock_operation = Mock()

    class TestTransformer(CASTableTransformer):
        def execute(self, input_table):
            return Ok(input_table)

    transformer = TestTransformer(mock_operation)

    assert transformer.operation is mock_operation


def test_transformer_execute_signature() -> None:
    """Test that execute method has correct signature."""

    class TestTransformer(CASTableTransformer):
        def execute(self, input_table):
            # Use the operation
            return Ok(input_table)

    import inspect

    sig = inspect.signature(TestTransformer.execute)

    # Should have self and input_table parameters
    params = list(sig.parameters.keys())
    assert "self" in params
    assert "input_table" in params
