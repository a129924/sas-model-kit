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
    for custom code execution and processing options.

    Attributes:
        source_caslib: Source data CAS library
        source_table: Source data CAS table
        target_caslib: Target output CAS library
        target_table: Target output CAS table
        code: SAS DATA step code to execute
        max_threads: Maximum number of threads for parallel processing

    Examples:
        >>> param = DataStepParameter(
        ...     source_caslib="public",
        ...     source_table="raw_data",
        ...     target_caslib="public",
        ...     target_table="processed_data",
        ...     code="data output; set input; new_var = var1 * 2; run;",
        ...     max_threads=4,
        ... )
        >>> param.validate()
    """

    code: str
    max_threads: int = 1

    @override
    def validate(self) -> None:
        """Validate DATA step parameter values.

        Raises:
            ValueError: If required parameters are invalid

        Note:
            Validates base parameters first, then DATA step specific fields.
        """
        super().validate()

        if not self.code:
            msg = "code cannot be empty"
            raise ValueError(msg)

        if self.max_threads < 1:
            msg = f"max_threads must be >= 1, got {self.max_threads}"
            raise ValueError(msg)
