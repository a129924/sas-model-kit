"""Tests for Model types and enumerations."""

from __future__ import annotations

from sas_model_kit.model.types import ModelTableType


class TestModelTableType:
    """Test ModelTableType enumeration."""

    def test_astore_value(self) -> None:
        """Test ASTORE enum value."""
        assert ModelTableType.ASTORE.value == "ASTORE"
        assert str(ModelTableType.ASTORE) == "ASTORE"

    def test_datastep_value(self) -> None:
        """Test DATASTEP enum value."""
        assert ModelTableType.DATASTEP.value == "DATASTEP"
        assert str(ModelTableType.DATASTEP) == "DATASTEP"

    def test_string_comparison(self) -> None:
        """Test that enum can be compared with strings."""
        assert ModelTableType.ASTORE == "ASTORE"
        assert ModelTableType.DATASTEP == "DATASTEP"

    def test_all_members(self) -> None:
        """Test all enum members are defined."""
        members = list(ModelTableType)
        assert len(members) == 2
        assert ModelTableType.ASTORE in members
        assert ModelTableType.DATASTEP in members

    def test_enum_is_string(self) -> None:
        """Test that enum inherits from str."""
        assert isinstance(ModelTableType.ASTORE, str)
        assert isinstance(ModelTableType.DATASTEP, str)

    def test_usage_in_dict(self) -> None:
        """Test enum can be used as dict key and value."""
        config = {
            "model_type": ModelTableType.ASTORE,
            ModelTableType.DATASTEP: "some_value",
        }
        assert config["model_type"] == ModelTableType.ASTORE
        assert config[ModelTableType.DATASTEP] == "some_value"

    def test_serialization(self) -> None:
        """Test enum serialization to string."""
        model_type = ModelTableType.ASTORE
        # Can be serialized directly
        assert f"Type: {model_type}" == "Type: ASTORE"
