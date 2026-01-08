"""SWAT-specific parameter mappers for processor layer (Bounded Context).

This module provides parameter mappers for the processor layer, adapting
domain parameters to SWAT action dictionaries. It reuses mappers from
the model layer while remaining independent.

Design:
    - Wraps model layer mappers (ExplainParameterToSwatDictMapper)
    - Processor-specific interface (build_action_dict)
    - Decouples processor from model layer implementation details
"""

from __future__ import annotations

from typing import Any

from sas_model_kit.model.mapper.swat import ExplainParameterToSwatDictMapper
from sas_model_kit.parameter import ExplainParameter


class SwatExplainParameterMapper:
    """Map ExplainParameter to SWAT action dictionary (processor layer).

    This mapper wraps the model layer's ExplainParameterToSwatDictMapper,
    providing a processor-specific interface. It allows processor layer
    to build call_action dictionaries without directly depending on
    model layer mappers.

    Example:
        >>> mapper = SwatExplainParameterMapper()
        >>> action_dict = mapper.build_action_dict(
        ...     parameter=explain_param,
        ...     where="id=123",
        ... )
        >>> result = operation.call_action(
        ...     "explainModel.shapleyExplainer",
        ...     **action_dict
        ... )
    """

    def __init__(self) -> None:
        """Initialize mapper with model layer adapter."""
        self._mapper = ExplainParameterToSwatDictMapper()

    def build_action_dict(
        self,
        parameter: ExplainParameter,
        **context: Any,
    ) -> dict[str, Any]:
        """Build call_action dictionary for explainModel.shapleyExplainer.

        Args:
            parameter: ExplainParameter with model and feature configuration
            **context: Additional context (e.g., where clause customizations)

        Returns:
            Dictionary suitable for operation.call_action(**result)

        Example:
            >>> mapper = SwatExplainParameterMapper()
            >>> action_dict = mapper.build_action_dict(
            ...     parameter=param,
            ...     where="id='customer_123'",
            ... )
        """
        return self._mapper.map(parameter, **context)
