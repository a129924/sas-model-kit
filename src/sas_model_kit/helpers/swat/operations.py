"""Compatibility module for legacy SWAT operations imports."""

from __future__ import annotations

from sas_model_kit.helpers.swat.action_processor import SWATActionProcessor
from sas_model_kit.helpers.swat.table_lifecycle import SWATTableLifecycle
from sas_model_kit.helpers.swat.table_metadata import SWATTableMetadata
from sas_model_kit.helpers.swat.table_transform import SWATTableTransform

__all__ = [
    "SWATActionProcessor",
    "SWATTableLifecycle",
    "SWATTableMetadata",
    "SWATTableTransform",
]
