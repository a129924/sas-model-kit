"""Tests for BaseModelParameter abstract class."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from sas_model_kit.parameter import BaseModelParameter


@dataclass(frozen=True)
class ConcreteParameter(BaseModelParameter):
    """Concrete implementation for testing."""

    def validate(self) -> None:
        """Implement abstract validate method."""
        super().validate()


def test_base_parameter_is_abstract() -> None:
    """Test that BaseModelParameter cannot be instantiated directly."""
    # Should not raise when creating concrete subclass
    param = ConcreteParameter(
        source_caslib="lib1",
        source_table="table1",
        target_caslib="lib2",
        target_table="table2",
    )
    assert param is not None


def test_base_parameter_validates_source_caslib() -> None:
    """Test validation of source_caslib field."""
    param = ConcreteParameter(
        source_caslib="",  # Invalid: empty
        source_table="table1",
        target_caslib="lib2",
        target_table="table2",
    )

    with pytest.raises(ValueError, match="source_caslib cannot be empty"):
        param.validate()


def test_base_parameter_validates_source_table() -> None:
    """Test validation of source_table field."""
    param = ConcreteParameter(
        source_caslib="lib1",
        source_table="",  # Invalid: empty
        target_caslib="lib2",
        target_table="table2",
    )

    with pytest.raises(ValueError, match="source_table cannot be empty"):
        param.validate()


def test_base_parameter_validates_target_caslib() -> None:
    """Test validation of target_caslib field."""
    param = ConcreteParameter(
        source_caslib="lib1",
        source_table="table1",
        target_caslib="",  # Invalid: empty
        target_table="table2",
    )

    with pytest.raises(ValueError, match="target_caslib cannot be empty"):
        param.validate()


def test_base_parameter_validates_target_table() -> None:
    """Test validation of target_table field."""
    param = ConcreteParameter(
        source_caslib="lib1",
        source_table="table1",
        target_caslib="lib2",
        target_table="",  # Invalid: empty
    )

    with pytest.raises(ValueError, match="target_table cannot be empty"):
        param.validate()


def test_base_parameter_successful_validation() -> None:
    """Test successful validation with all valid fields."""
    param = ConcreteParameter(
        source_caslib="lib1",
        source_table="table1",
        target_caslib="lib2",
        target_table="table2",
    )

    # Should not raise
    param.validate()


def test_base_parameter_immutability() -> None:
    """Test that parameter instances are immutable (frozen)."""
    param = ConcreteParameter(
        source_caslib="lib1",
        source_table="table1",
        target_caslib="lib2",
        target_table="table2",
    )

    with pytest.raises(AttributeError):
        param.source_caslib = "modified"  # type: ignore[misc]


def test_base_parameter_equality() -> None:
    """Test equality comparison of parameter instances."""
    param1 = ConcreteParameter(
        source_caslib="lib1",
        source_table="table1",
        target_caslib="lib2",
        target_table="table2",
    )
    param2 = ConcreteParameter(
        source_caslib="lib1",
        source_table="table1",
        target_caslib="lib2",
        target_table="table2",
    )
    param3 = ConcreteParameter(
        source_caslib="lib1",
        source_table="table1",
        target_caslib="lib3",  # Different
        target_table="table2",
    )

    assert param1 == param2
    assert param1 != param3
