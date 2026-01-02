"""Tests for BaseModelParameter abstract class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import pytest

from sas_model_kit.parameter import BaseModelParameter


@dataclass(frozen=True)
class MinimalParameter(BaseModelParameter):
    """Minimal concrete implementation for testing base functionality."""

    test_field: str = "test"

    def validate(self) -> None:
        """Implement abstract validate method."""
        if not self.test_field:
            msg = "test_field cannot be empty"
            raise ValueError(msg)


def test_base_parameter_is_abstract() -> None:
    """Test that BaseModelParameter cannot be instantiated directly."""
    # BaseModelParameter has abstract method validate(), so direct instantiation fails
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BaseModelParameter()  # type: ignore[abstract]


def test_base_parameter_concrete_implementation() -> None:
    """Test that concrete subclasses can be instantiated."""
    # Should not raise when creating concrete subclass
    param = MinimalParameter(test_field="value")
    assert param is not None
    assert param.test_field == "value"


def test_base_parameter_concrete_implementation_validation() -> None:
    """Test that concrete subclass validate() can be called."""
    param = MinimalParameter(test_field="valid_value")

    # Should not raise
    param.validate()


def test_base_parameter_concrete_implementation_invalid() -> None:
    """Test that concrete subclass validate() rejects invalid data."""
    param = MinimalParameter(test_field="")  # Invalid: empty

    with pytest.raises(ValueError, match="test_field cannot be empty"):
        param.validate()


def test_base_parameter_immutability() -> None:
    """Test that parameter instances are immutable (frozen)."""
    param = MinimalParameter(test_field="value")

    with pytest.raises(AttributeError):
        param.test_field = "modified"  # type: ignore[misc]


def test_base_parameter_equality() -> None:
    """Test equality comparison of parameter instances."""
    param1 = MinimalParameter(test_field="value")
    param2 = MinimalParameter(test_field="value")
    param3 = MinimalParameter(test_field="different")

    assert param1 == param2
    assert param1 != param3


def test_base_parameter_repr() -> None:
    """Test string representation of parameter instances."""
    param = MinimalParameter(test_field="value")
    repr_str = repr(param)

    # Should contain class name and fields
    assert "MinimalParameter" in repr_str
    assert "test_field" in repr_str
    assert "value" in repr_str


def test_base_parameter_inheritance() -> None:
    """Test that parameter classes must inherit from BaseModelParameter."""
    # Verify that concrete implementations inherit from BaseModelParameter
    param = MinimalParameter(test_field="value")
    assert isinstance(param, BaseModelParameter)
