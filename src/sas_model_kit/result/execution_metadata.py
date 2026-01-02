"""Execution metadata for model execution results.

This module defines the metadata structure that accompanies every model execution,
tracking performance and execution details without duplicating output location information.

Design Decision:
    ExecutionMetadata contains execution-level information only:
    - execution_time_ms: How long the execution took
    - rows_affected: Number of rows processed/created
    - (optional) intended_output_*: Only when NO CASTable data exists

    It explicitly does NOT contain output_caslib/output_table because:
    1. ModelResult.data (CASTableResult) already has these via CASTable.caslib/name
    2. Duplicating them creates inconsistency and maintenance burden
    3. For models with no data output, intended_output_* provides fallback info

    This follows Single Responsibility Principle:
    - ModelResult.data: represents actual output data and location
    - ModelResult.metadata: represents execution details
    - No redundancy, clear separation of concerns
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionMetadata:
    """Metadata about a model execution.

    Contains execution-level information such as timing and row counts.
    Does NOT duplicate output location information (use ModelResult.data.caslib instead).

    Attributes:
        execution_time_ms: Time taken to execute the model in milliseconds.
                          Must be non-negative.
        rows_affected: Number of rows processed or created during execution.
                      Must be non-negative. For some operations, may be 0 if
                      only metadata was computed.
        intended_output_caslib: (Optional) Intended output CAS library when no data is produced.
                               Use only when ModelResult.data is None. Must be paired with
                               intended_output_table if either is specified.
        intended_output_table: (Optional) Intended output CAS table name when no data is produced.
                              Use only when ModelResult.data is None. Must be paired with
                              intended_output_caslib if either is specified.

    Examples:
        >>> # Basic execution metadata
        >>> metadata = ExecutionMetadata(
        ...     execution_time_ms=150.5,
        ...     rows_affected=1000,
        ... )

        >>> # With intended output location (for no-data scenarios)
        >>> metadata_with_intended = ExecutionMetadata(
        ...     execution_time_ms=250.0,
        ...     rows_affected=0,  # No data was produced
        ...     intended_output_caslib="public",
        ...     intended_output_table="explain_results",
        ... )

        >>> # Immutable: parameter is frozen
        >>> metadata.execution_time_ms = 200  # Raises AttributeError
    """

    execution_time_ms: float
    rows_affected: int
    intended_output_caslib: str | None = None
    intended_output_table: str | None = None

    def __post_init__(self) -> None:
        """Validate metadata after initialization.

        Raises:
            ValueError: If values are invalid or constraints are violated
        """
        if self.execution_time_ms < 0:
            msg = (
                f"execution_time_ms must be non-negative, got {self.execution_time_ms}"
            )
            raise ValueError(msg)

        if self.rows_affected < 0:
            msg = f"rows_affected must be non-negative, got {self.rows_affected}"
            raise ValueError(msg)

        # Validate intended output pairing
        has_intended_caslib = self.intended_output_caslib is not None and bool(
            self.intended_output_caslib
        )
        has_intended_table = self.intended_output_table is not None and bool(
            self.intended_output_table
        )

        if has_intended_caslib != has_intended_table:
            msg = (
                "intended_output_caslib and intended_output_table must both be "
                "provided or both be None"
            )
            raise ValueError(msg)
