"""Base parameter class for model execution.

This module defines the abstract base class for all model parameters,
establishing the common interface and required fields.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class BaseModelParameter(ABC):
    """Abstract base class for model execution parameters.

    Provides common fields for source and target specifications
    that all model parameters must include. Uses frozen dataclass
    to ensure immutability.

    Attributes:
        source_caslib: Source CAS library name
        source_table: Source CAS table name
        target_caslib: Target CAS library name for output
        target_table: Target CAS table name for output

    Examples:
        >>> @dataclass(frozen=True)
        ... class CustomParameter(BaseModelParameter):
        ...     custom_field: str
        ...
        ...     def validate(self) -> None:
        ...         if not self.custom_field:
        ...             raise ValueError("custom_field required")
    """

    source_caslib: str
    source_table: str
    target_caslib: str
    target_table: str

    @abstractmethod
    def validate(self) -> None:
        """Validate parameter values.

        Raises:
            ValueError: If any parameter value is invalid

        Note:
            Concrete implementations must call super().validate()
            to ensure base validation is performed.
        """
        if not self.source_caslib:
            msg = "source_caslib cannot be empty"
            raise ValueError(msg)
        if not self.source_table:
            msg = "source_table cannot be empty"
            raise ValueError(msg)
        if not self.target_caslib:
            msg = "target_caslib cannot be empty"
            raise ValueError(msg)
        if not self.target_table:
            msg = "target_table cannot be empty"
            raise ValueError(msg)
