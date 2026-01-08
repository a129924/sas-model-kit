"""SWAT processor package (Bounded Context).

This package contains SWAT-specific implementations for the processor layer,
following Bounded Context design from Domain-Driven Design.

Modules:
    - mappers: Parameter mappers for SWAT actions
"""

from sas_model_kit.processor.swat.mappers import SwatExplainParameterMapper

__all__ = ["SwatExplainParameterMapper"]
