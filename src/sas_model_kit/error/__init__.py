"""Public error API for SAS Model Kit."""

from .base import BaseError, ErrorProtocol, ErrorSeverity
from .data import (
    ColumnNotFoundError,
    DataError,
    DataErrorCode,
    DataTypeMismatchError,
    InvalidDataError,
    SchemaMismatchError,
)
from .datasource import DataFetchFailure, UploadFailure
from .operation import OperationError, OperationErrorCode, TableNotFoundError
from .parameter import (
    ConflictingRuleFailure,
    InvalidTypeFailure,
    MissingFieldFailure,
    ValidationFailure,
)
from .transformer import (
    DuplicateKeyError,
    SortError,
    TransformationFailure,
)

__all__ = [
    "BaseError",
    "ErrorProtocol",
    "ErrorSeverity",
    "OperationError",
    "OperationErrorCode",
    "TableNotFoundError",
    "DataErrorCode",
    "DataError",
    "ColumnNotFoundError",
    "SchemaMismatchError",
    "DataTypeMismatchError",
    "InvalidDataError",
    "UploadFailure",
    "DataFetchFailure",
    "TransformationFailure",
    "SortError",
    "DuplicateKeyError",
    "ValidationFailure",
    "MissingFieldFailure",
    "InvalidTypeFailure",
    "ConflictingRuleFailure",
]
