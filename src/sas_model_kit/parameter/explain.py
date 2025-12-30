"""Explain model parameter for model explainability analysis.

This module provides parameters for generating model explanations,
including visualization options and analysis depth configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from typing_extensions import override

from .base import BaseModelParameter


class ExplainDepth(Enum):
    """Depth level for explanation analysis.

    Attributes:
        BASIC: Basic explanations only
        DETAILED: Detailed analysis with feature importance
        FULL: Full analysis including interactions
    """

    BASIC = "basic"
    DETAILED = "detailed"
    FULL = "full"


@dataclass(frozen=True)
class ExplainParameter(BaseModelParameter):
    """Parameters for model explainability analysis.

    Extends BaseModelParameter with explanation-specific configuration
    for visualization output and analysis depth.

    Attributes:
        source_caslib: Source data CAS library
        source_table: Source data CAS table
        target_caslib: Target output CAS library
        target_table: Target output CAS table
        depth: Analysis depth level
        generate_plots: Whether to generate visualization plots

    Examples:
        >>> param = ExplainParameter(
        ...     source_caslib="public",
        ...     source_table="test_data",
        ...     target_caslib="public",
        ...     target_table="explanations",
        ...     depth=ExplainDepth.DETAILED,
        ...     generate_plots=True,
        ... )
        >>> param.validate()
    """

    depth: ExplainDepth = ExplainDepth.BASIC
    generate_plots: bool = False

    @override
    def validate(self) -> None:
        """Validate explain parameter values.

        Raises:
            ValueError: If required parameters are invalid

        Note:
            Validates base parameters first, then explanation-specific fields.
        """
        super().validate()

        if not isinstance(self.depth, ExplainDepth):
            msg = f"depth must be ExplainDepth enum, got {type(self.depth)}"
            raise ValueError(msg)
