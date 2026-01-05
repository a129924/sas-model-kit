"""
Result layer for SAS Model Kit.

This module provides result types and protocols for model execution results,
following the Single Responsibility Principle (SRP).
"""

from sas_model_kit.result.base import Err, Ok, Result
from sas_model_kit.result.cas_table import CASTableResult
from sas_model_kit.result.execution_metadata import ExecutionMetadata
from sas_model_kit.result.model_result import ModelResult
from sas_model_kit.result.model_types import ModelError, ModelSuccess
from sas_model_kit.result.status import ResultStatus
from sas_model_kit.result.streamable import StreamableResult
from sas_model_kit.result.swat_result import SwatModelResult
from sas_model_kit.result.transformation_result import TransformationResult

__all__ = [
    "Ok",
    "Result",
    "Err",
    "CASTableResult",
    "ExecutionMetadata",
    "ModelError",
    "ModelResult",
    "ModelSuccess",
    "ResultStatus",
    "StreamableResult",
    "SwatModelResult",
    "TransformationResult",
]
