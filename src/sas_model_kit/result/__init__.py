"""Result layer for SAS Model Kit.

This module provides result types and protocols for model execution results,
following the Single Responsibility Principle (SRP).
"""

from typing import TYPE_CHECKING, Any

from sas_model_kit.error import (
    ConflictingRuleFailure,
    DataFetchFailure,
    DuplicateKeyError,
    ErrorSeverity,
    InvalidTypeFailure,
    MissingFieldFailure,
    OperationError,
    SortError,
    TransformationFailure,
    UploadFailure,
    ValidationFailure,
)
from sas_model_kit.result.base import Err, Ok, Result
from sas_model_kit.result.cas_table import CASTableResult
from sas_model_kit.result.execution_metadata import ExecutionMetadata
from sas_model_kit.result.model_result import ModelResult
from sas_model_kit.result.model_types import ModelError, ModelSuccess
from sas_model_kit.result.status import ResultStatus
from sas_model_kit.result.streamable import StreamableResult
from sas_model_kit.result.swat_result import SwatModelResult
from sas_model_kit.result.transformation_result import TransformationResult

try:  # pragma: no cover - optional dependency
    from swat import CASTable
except ImportError:  # pragma: no cover
    CASTable = Any  # type: ignore[misc]

if TYPE_CHECKING:  # pragma: no cover
    from swat import CASTable as _CASTable

    CASTable = _CASTable

# Union-based Result aliases for boundary layers
OperationResult = Result[Any, OperationError]
UploadResult = Result[None, UploadFailure]
FetchResult = Result[Any, DataFetchFailure]
TransformationExecutionResult = Result[
    CASTable, SortError | DuplicateKeyError | OperationError
]
SortExecutionResult = Result[CASTable, SortError | OperationError]
UniqueKeyExecutionResult = Result[CASTable, DuplicateKeyError | OperationError]
ValidationResult = Result[
    None,
    MissingFieldFailure
    | InvalidTypeFailure
    | ConflictingRuleFailure
    | ValidationFailure,
]

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
    "ErrorSeverity",
    "OperationResult",
    "UploadResult",
    "FetchResult",
    "TransformationExecutionResult",
    "SortExecutionResult",
    "UniqueKeyExecutionResult",
    "ValidationResult",
    "ConflictingRuleFailure",
    "DataFetchFailure",
    "DuplicateKeyError",
    "InvalidTypeFailure",
    "MissingFieldFailure",
    "OperationError",
    "SortError",
    "TransformationFailure",
    "UploadFailure",
    "ValidationFailure",
]
