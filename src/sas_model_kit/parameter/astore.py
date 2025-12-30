"""Astore model parameter for ASTORE execution.

This module provides parameters for executing ASTORE models,
including model store specification and optional code configuration.
"""

from __future__ import annotations

from dataclasses import dataclass

from typing_extensions import override

from .base import BaseModelParameter


@dataclass(frozen=True)
class AstoreParameter(BaseModelParameter):
    """Parameters for ASTORE model execution.

    Extends BaseModelParameter with ASTORE-specific fields for
    model store location and optional code configuration.

    Attributes:
        source_caslib: Source data CAS library
        source_table: Source data CAS table
        target_caslib: Target output CAS library
        target_table: Target output CAS table
        model_caslib: Model store CAS library
        model_table: Model store CAS table (ASTORE)
        code_caslib: Optional code CAS library
        code_table: Optional code CAS table

    Examples:
        >>> param = AstoreParameter(
        ...     source_caslib="public",
        ...     source_table="input_data",
        ...     target_caslib="public",
        ...     target_table="scored_data",
        ...     model_caslib="models",
        ...     model_table="my_astore",
        ... )
        >>> param.validate()
    """

    model_caslib: str
    model_table: str
    code_caslib: str = ""
    code_table: str = ""

    @override
    def validate(self) -> None:
        """Validate ASTORE parameter values.

        Raises:
            ValueError: If required parameters are empty or invalid

        Note:
            Validates base parameters first, then ASTORE-specific fields.
        """
        super().validate()

        if not self.model_caslib:
            msg = "model_caslib cannot be empty"
            raise ValueError(msg)
        if not self.model_table:
            msg = "model_table cannot be empty"
            raise ValueError(msg)

        # code_caslib and code_table are optional
        # But if one is provided, both should be provided
        if bool(self.code_caslib) != bool(self.code_table):
            msg = "Both code_caslib and code_table must be provided together"
            raise ValueError(msg)
