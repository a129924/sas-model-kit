"""DataStep parameter for custom DATA step execution.

This module provides parameters for executing custom SAS DATA step code.
The developer writes complete code but must specify output locations.
\"\"\"
"""

from __future__ import annotations

from dataclasses import dataclass

from typing_extensions import override

from .base import BaseModelParameter


@dataclass(frozen=True)
class DataStepParameter(BaseModelParameter):
    """Parameters for DATA step execution.

    Contains complete SAS DATA step code plus explicit output location.
    Developer writes the code; framework requires output location spec.

    Attributes:
        score_code: Complete SAS DATA step code including SET/{logic}/RUN
        output_caslib: Output CAS library name (REQUIRED)
        output_table: Output table name (REQUIRED)

    Examples:
        >>> param = DataStepParameter(
        ...     score_code='''
        ...         data public.results;
        ...           set public.raw_data;
        ...           new_var = var1 * 2;
        ...         run;
        ...     ''',
        ...     output_caslib="public",
        ...     output_table="results"
        ... )
        >>> param.validate()
    """

    score_code: str
    output_caslib: str
    output_table: str

    @override
    def validate(self) -> None:
        """Validate DATA step parameter values.

        Raises:
            ValueError: If required parameters are invalid
        """
        if not self.score_code:
            msg = "score_code cannot be empty"
            raise ValueError(msg)
        if not isinstance(self.score_code, str):
            msg = "score_code must be a string"
            raise ValueError(msg)

        if not self.output_caslib:
            msg = "output_caslib cannot be empty"
            raise ValueError(msg)
        if not self.output_table:
            msg = "output_table cannot be empty"
            raise ValueError(msg)
