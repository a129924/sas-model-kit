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
    model store location and SAS evaluation code.

    Attributes:
        source_caslib: Source data CAS library
        source_table: Source data CAS table
        target_caslib: Target output CAS library
        target_table: Target output CAS table
        model_caslib: Model store CAS library (where ASTORE is stored)
        model_table: Model store CAS table (ASTORE binary model)
        score_code: SAS evaluation code (from dmcas_epscorecode.sas)

    Examples:
        >>> param = AstoreParameter(
        ...     source_caslib="public",
        ...     source_table="input_data",
        ...     target_caslib="public",
        ...     target_table="scored_data",
        ...     model_caslib="models",
        ...     model_table="my_astore",
        ...     score_code="proc astore; ... run;",
        ... )
        >>> param.validate()
    """

    model_caslib: str
    model_table: str
    score_code: str

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

        if not self.score_code:
            msg = "score_code cannot be empty"
            raise ValueError(msg)
