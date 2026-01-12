"""Deprecation wrapper for BatchExplainProcessor.

DEPRECATED: BatchExplainProcessor has been moved to processor.swat.explain
as part of the SWAT-specific Bounded Context reorganization.

This module provides backward compatibility by re-exporting from the new location.

Migration path:
    OLD: from sas_model_kit.processor import BatchExplainProcessor
    NEW: from sas_model_kit.processor.swat import BatchExplainProcessor
"""

from __future__ import annotations

import warnings

# Re-export from new SWAT-specific location
from sas_model_kit.processor.swat.explain import BatchExplainProcessor

__all__ = ["BatchExplainProcessor"]

# Deprecation warning when imported from old location
warnings.warn(
    "Importing BatchExplainProcessor from sas_model_kit.processor.explain is deprecated. "
    "Use sas_model_kit.processor.swat.explain instead. "
    "This import will be removed in v0.4.0.",
    DeprecationWarning,
    stacklevel=2,
)
