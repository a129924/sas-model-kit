"""DataStep parameter for custom DATA step execution.

This module provides parameters for executing custom SAS DATA step code
with configurable processing options.
"""

from __future__ import annotations

from dataclasses import dataclass

from typing_extensions import override

from .base import BaseModelParameter


@dataclass(frozen=True)
class DataStepParameter(BaseModelParameter):
    """Parameters for DATA step execution.

    Extends BaseModelParameter with DATA step specific configuration
    for custom code execution.

    Attributes:
        source_caslib: Source data CAS library
        source_table: Source data CAS table
        target_caslib: Target output CAS library
        target_table: Target output CAS table
        score_code: SAS DATA step code to execute (from dmcas_scorecode.sas)

    Examples:
        >>> param = DataStepParameter(
        ...     source_caslib="public",
        ...     source_table="raw_data",
        ...     target_caslib="public",
        ...     target_table="processed_data",
        ...     score_code="new_var = var1 * 2;",
        ... )
        >>> param.validate()
    """

    score_code: str

    @override
    def validate(self) -> None:
        """Validate DATA step parameter values.

        Raises:
            ValueError: If required parameters are invalid

        Note:
            Validates base parameters first, then DATA step specific fields.
        """
        super().validate()

        if not self.score_code:
            msg = "score_code cannot be empty"
            raise ValueError(msg)
