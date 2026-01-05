"""Transformer package initialization.

This package provides CAS table transformation operations following CSRP
(Concrete Single Responsibility Principle). Each transformer handles a
specific transformation type.

Exports:
    - CASTableTransformer: Abstract base class for all transformers
    - TransformationError: Base exception for transformation errors
    - Specific exceptions: InvalidColumnError, TableNotFoundError, etc.
"""

from .exceptions import (
    ColumnConflictError,
    InvalidColumnError,
    TableNotFoundError,
    TransformationError,
)
from .protocol import CASTableTransformer
from .sort import SortTransformer

__all__ = [
    "CASTableTransformer",
    "TransformationError",
    "InvalidColumnError",
    "TableNotFoundError",
    "ColumnConflictError",
    "SortTransformer",
]
