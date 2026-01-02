"""Base parameter class for model execution.

This module defines the abstract base class for all model parameters,
establishing the validation interface without concrete field requirements.

Design Decision:
    BaseModelParameter is a pure validation framework with NO concrete fields.
    Each Model parameter class (AstoreParameter, DataStepParameter, ExplainParameter)
    defines its own fields based on specific needs, following SRP (Single Responsibility
    Principle). This avoids forcing unrelated fields on parameter classes that don't
    use them.

    Example:
        - AstoreParameter needs: input_*/model_*/score_code (3 layers)
        - DataStepParameter needs: score_code only (1 layer)
        - ExplainParameter needs: train_*/score_*/model_* (different combination)

    A shared base with source_*/target_* would violate SRP and add unnecessary coupling.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class BaseModelParameter(ABC):
    """Abstract base class for model execution parameters.

    Serves as a validation framework for all model parameters.
    Concrete parameter classes must implement validate() to check
    their specific field requirements.

    Uses frozen dataclass to ensure immutability of parameters
    after construction.

    Examples:
        >>> @dataclass(frozen=True)
        ... class CustomParameter(BaseModelParameter):
        ...     input_table: str
        ...     custom_field: str
        ...
        ...     def validate(self) -> None:
        ...         if not self.input_table:
        ...             raise ValueError("input_table required")
        ...         if not self.custom_field:
        ...             raise ValueError("custom_field required")
    """

    @abstractmethod
    def validate(self) -> None:
        """Validate parameter values.

        Each concrete parameter class must implement this method to validate
        its own fields. There is no shared validation logic in the base class
        because each parameter class has different field requirements.

        Raises:
            ValueError: If any parameter value is invalid

        Examples:
            >>> param = AstoreParameter(...)
            >>> param.validate()  # Raises ValueError if fields invalid
        """
