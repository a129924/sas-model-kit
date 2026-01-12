"""SWAT processor package (Bounded Context).

This package contains SWAT-specific implementations for the processor layer,
following Bounded Context design from Domain-Driven Design.

Modules:
    - mappers: Parameter mappers for SWAT actions
    - explain: Batch processor for Shapley Explainer
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sas_model_kit.processor.swat.explain import BatchExplainProcessor
    from sas_model_kit.processor.swat.mappers import SwatExplainParameterMapper

__all__ = ["BatchExplainProcessor", "SwatExplainParameterMapper"]


def __getattr__(name: str):
    """Lazy import to avoid circular dependencies."""
    if name == "BatchExplainProcessor":
        from sas_model_kit.processor.swat.explain import BatchExplainProcessor

        return BatchExplainProcessor
    if name == "SwatExplainParameterMapper":
        from sas_model_kit.processor.swat.mappers import SwatExplainParameterMapper

        return SwatExplainParameterMapper
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
