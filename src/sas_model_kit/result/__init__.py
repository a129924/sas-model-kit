"""
Result layer for SAS Model Kit.

This module provides result types and protocols for model execution results,
following the Single Responsibility Principle (SRP).
"""

from sas_model_kit.result.cas_table import CASTableResult
from sas_model_kit.result.model_result import ModelResult
from sas_model_kit.result.status import ResultStatus
from sas_model_kit.result.streamable import StreamableResult
from sas_model_kit.result.swat_result import SwatModelResult

__all__ = [
    "CASTableResult",
    "ModelResult",
    "ResultStatus",
    "StreamableResult",
    "SwatModelResult",
]
