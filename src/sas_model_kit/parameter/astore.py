"""Astore model parameter for ASTORE execution.

This module provides parameters for executing ASTORE models,
including input data, model store specification, and optional output configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from typing_extensions import override

from .base import BaseModelParameter


@dataclass(frozen=True)
class AstoreParameter(BaseModelParameter):
    """Parameters for ASTORE model execution.

    Contains three layers of information:
    1. Input data: input_caslib, input_table (the data to score)
    2. Model location: model_caslib, model_table (the ASTORE binary model)
    3. Score code: DS2 code extracted from the model
    4. Optional output: casout (CAS output specification for result table)

    The framework automatically manages output location if casout is None.

    Attributes:
        input_caslib: Source data CAS library
        input_table: Source data CAS table
        model_caslib: Model store CAS library (where ASTORE is stored)
        model_table: Model store CAS table (ASTORE binary model)
        score_code: DS2 evaluation code (from dmcas_epscorecode.sas)
        casout: Optional CAS output configuration dict. If None, framework
                auto-generates with default settings. Supports keys:
                {name, caslib, replace, promote, backup}

    Examples:
        >>> param = AstoreParameter(
        ...     input_caslib="public",
        ...     input_table="input_data",
        ...     model_caslib="models",
        ...     model_table="my_astore",
        ...     score_code="proc astore; ... run;",
        ...     casout=None,  # Framework will auto-generate output location
        ... )
        >>> param.validate()

        >>> # Advanced: custom output configuration
        >>> param_custom = AstoreParameter(
        ...     input_caslib="public",
        ...     input_table="input_data",
        ...     model_caslib="models",
        ...     model_table="my_astore",
        ...     score_code="proc astore; ... run;",
        ...     casout={"name": "custom_output", "caslib": "public", "promote": True}
        ... )
    """

    input_caslib: str
    input_table: str
    model_caslib: str
    model_table: str
    score_code: str
    casout: dict[str, Any] | None = None

    @override
    def validate(self) -> None:
        """Validate ASTORE parameter values.

        Raises:
            ValueError: If required parameters are empty or invalid
        """
        # Validate input layer
        if not self.input_caslib:
            msg = "input_caslib cannot be empty"
            raise ValueError(msg)
        if not self.input_table:
            msg = "input_table cannot be empty"
            raise ValueError(msg)

        # Validate model layer
        if not self.model_caslib:
            msg = "model_caslib cannot be empty"
            raise ValueError(msg)
        if not self.model_table:
            msg = "model_table cannot be empty"
            raise ValueError(msg)

        # Validate score code
        if not self.score_code:
            msg = "score_code cannot be empty"
            raise ValueError(msg)

        # Validate casout if provided
        if self.casout is not None:
            if not isinstance(self.casout, dict):
                msg = "casout must be a dictionary or None"
                raise ValueError(msg)
            if "name" not in self.casout or not self.casout["name"]:
                msg = "casout['name'] is required when casout is provided"
                raise ValueError(msg)
