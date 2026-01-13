"""Transformation result type alias.

This module defines the TransformationResult type alias for Transformer layer
operations. It provides explicit semantics separate from ModelResult.

Type Alias:
    TransformationResult = Result[CASTable, TransformationError]

    - Success (Ok): Contains a CASTable
    - Failure (Err): Contains a TransformationError

Design Decision:
    - Lightweight: No ExecutionMetadata (that's for Model layer)
    - Explicit: Clear distinction from ModelResult
    - Type-safe: Enforces proper error types

Examples:
    >>> from sas_model_kit.transformer.exceptions import TransformationError
    >>> from sas_model_kit.result.base import Ok, Err
    >>>
    >>> # Success
    >>> result: TransformationResult = Ok(sorted_table)
    >>>
    >>> # Failure
    >>> result: TransformationResult = Err(TransformationError("Sort failed"))
"""

from typing import TYPE_CHECKING, TypeAlias

try:
    from swat import CASTable
except ImportError as e:
    raise ImportError(
        "swat package is required for TransformationResult. "
        "Please install it via 'pip install swat'."
    ) from e

from ..result.base import Result

if TYPE_CHECKING:  # pragma: no cover
    from ..transformer.exceptions import TransformationError

# Type alias for explicit semantics (use string annotation to avoid circular import)
TransformationResult: TypeAlias = "Result[CASTable, TransformationError]"

__all__ = ["TransformationResult"]
