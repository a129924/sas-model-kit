"""Public error API for SAS Model Kit."""

from .base import BaseError, ErrorProtocol, ErrorSeverity
from .datasource import DataFetchFailure, UploadFailure
from .operation import OperationError
from .parameter import (
    ConflictingRuleFailure,
    InvalidTypeFailure,
    MissingFieldFailure,
    ValidationFailure,
)
from .transformer import (
    DuplicateKeyError,
    InvalidColumnFailure,
    SortError,
    TransformationFailure,
)

__all__ = [
    "BaseError",
    "ErrorProtocol",
    "ErrorSeverity",
    "OperationError",
    "UploadFailure",
    "DataFetchFailure",
    "TransformationFailure",
    "InvalidColumnFailure",
    "SortError",
    "DuplicateKeyError",
    "ValidationFailure",
    "MissingFieldFailure",
    "InvalidTypeFailure",
    "ConflictingRuleFailure",
]
