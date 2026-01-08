"""Batch processors.

Exports batch processing contracts and implementations.
"""

from typing import TYPE_CHECKING

from sas_model_kit.processor.base import (
    BaseBatchProcessor,
    ExecutionError,
    ExecutionItem,
    ExecutionSuccess,
    ProcessorError,
    ProcessorResult,
)
from sas_model_kit.processor.executor_batch import BatchOperationExecutor

if TYPE_CHECKING:
    from sas_model_kit.processor.explain import BatchExplainProcessor

__all__ = [
    "BaseBatchProcessor",
    "ExecutionSuccess",
    "ExecutionError",
    "ExecutionItem",
    "ProcessorError",
    "ProcessorResult",
    "BatchExplainProcessor",
    "BatchOperationExecutor",
]


def __getattr__(name: str):
    """Lazy import for backward compatibility."""
    if name == "BatchExplainProcessor":
        import warnings

        warnings.warn(
            "Importing BatchExplainProcessor from sas_model_kit.processor.explain is deprecated. "
            "Use sas_model_kit.processor.swat.explain instead. "
            "This import will be removed in v0.4.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        from sas_model_kit.processor.explain import BatchExplainProcessor

        return BatchExplainProcessor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
