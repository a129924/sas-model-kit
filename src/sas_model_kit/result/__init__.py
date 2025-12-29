"""
Result layer for SAS Model Kit.

This module provides result types and protocols for model execution results,
following the Single Responsibility Principle (SRP).
"""

from sas_model_kit.result.status import ResultStatus
from sas_model_kit.result.streamable import StreamableResult

__all__ = [
    "ResultStatus",
    "StreamableResult",
]
