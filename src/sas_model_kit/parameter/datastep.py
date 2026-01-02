"""DataStep parameter for custom DATA step execution.

This module provides parameters for executing custom SAS DATA step code.
Unlike AstoreParameter which specifies input/model/output separately,
DataStepParameter only holds the complete SAS code because the developer
has already written the full logic including input/output specifications.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from typing_extensions import override

from .base import BaseModelParameter


@dataclass(frozen=True)
class DataStepParameter(BaseModelParameter):
    """Parameters for DATA step execution.

    Contains a complete SAS DATA step code that the developer has written,
    including all input (SET statement) and output (DATA statement) specifications.

    Unlike AstoreParameter which has input_*/model_*/score_code layers,
    DataStepParameter is minimal because:
    1. The developer writes the complete code themselves
    2. Input/output locations are embedded in the code (data/set statements)
    3. The framework's responsibility is only to execute the code

    Attributes:
        score_code: Complete SAS DATA step code including data/set/{logic}/run;
                   Example: "data output_lib.output_table;
                             set input_lib.input_table;
                             new_var = var1 * 2;
                           run;"
        casout: Optional CAS output configuration (override). Usually not needed
               since output is already in score_code.

    Examples:
        >>> # Developer writes complete code
        >>> param = DataStepParameter(
        ...     score_code='''
        ...         data public.results;
        ...           set public.raw_data;
        ...           new_var = var1 * 2;
        ...         run;
        ...     ''',
        ... )
        >>> param.validate()

        >>> # No need to specify input_caslib, input_table, etc.
        >>> # All is in the code!
    """

    score_code: str
    casout: dict[str, Any] | None = None

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

        # Validate casout if provided
        if self.casout is not None:
            if not isinstance(self.casout, dict):
                msg = "casout must be a dictionary or None"
                raise ValueError(msg)
