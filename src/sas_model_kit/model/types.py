"""Model types and enumerations.

This module provides type definitions and enumerations for the Model layer,
following the Single Responsibility Principle (SRP).

Types:
    - ModelTableType: Enumeration for model table types (ASTORE, DATASTEP)

Examples:
    >>> from sas_model_kit.model.types import ModelTableType
    >>> model_type = ModelTableType.ASTORE
    >>> print(model_type)  # "ASTORE"
    >>> print(model_type.value)  # "ASTORE"
"""

from __future__ import annotations

from enum import Enum
from typing import TypedDict

from typing_extensions import Required


class ModelTableType(str, Enum):
    """Model table type enumeration for Explain parameter.

    Defines the supported model types for explainability analysis.
    Inherits from str to enable direct string comparison and serialization.

    Attributes:
        ASTORE: Analytic Store model type (binary model format)
        DATASTEP: DATA Step model type (SAS code-based model)

    Examples:
        >>> # Type-safe model type specification
        >>> model_type = ModelTableType.ASTORE
        >>> print(model_type)  # "ASTORE"
        >>> print(model_type.value)  # "ASTORE"

        >>> # String comparison works
        >>> if model_type == "ASTORE":
        ...     print("Using ASTORE model")

        >>> # Use in parameter
        >>> param = ExplainParameter(
        ...     model_table_type=ModelTableType.ASTORE,
        ...     ...
        ... )
    """

    ASTORE = "ASTORE"
    DATASTEP = "DATASTEP"

    def __str__(self) -> str:
        """String representation for SAS API calls.

        Returns:
            The string value of the enum member.

        Examples:
            >>> str(ModelTableType.ASTORE)
            'ASTORE'
        """
        return self.value


class ShapleyValues(TypedDict):
    """TypedDict for Shapley values representation.

    Represents the structure of Shapley values returned by explainModel actions.

    Attributes:
        Variable: Name of the feature variable
        ShapleyValue: Corresponding Shapley value for the variable
    Examples:
        >>> shapley: ShapleyValues = {
        ...     "Variable": "age",
        ...     "ShapleyValue": 0.25
        ... }
    """

    Variable: Required[str]
    ShapleyValue: Required[float]
