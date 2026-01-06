"""Model execution payload types.

This module provides payload dataclasses for model execution results,
following the Class Single Responsibility Principle (CSRP).

Each payload type represents the pure data returned by an Executor,
without error handling or metadata (those are handled by Model layer).

Types:
    - AstorePayload: Result data from ASTORE model execution
    - ExplainPayload: Result data from Explain model execution
    - DataStepPayload: Result data from DataStep execution

Design:
    - Frozen dataclasses for immutability
    - Pure data types (no business logic)
    - Executor layer returns these payloads
    - Model layer wraps them in Result[ModelSuccess[T], ModelError]

Examples:
    >>> # Executor returns pure payload
    >>> payload = AstorePayload(
    ...     output_caslib="public",
    ...     output_table="scored_data",
    ...     rows_scored=1000
    ... )
    >>>
    >>> # Model layer wraps in Result
    >>> from sas_model_kit.result import Ok, ModelSuccess
    >>> result = Ok(ModelSuccess(data=payload, metadata=...))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from sas_model_kit.model.types import ShapleyValues

try:
    from swat import CASTable
except ImportError:
    # CASTable is optional for type hints
    raise ImportError(
        "swat package is required for CASTable type hints. "
        "Install via 'pip install swat'."
    ) from ImportError


@dataclass(frozen=True)
class AstorePayload:
    """Payload from ASTORE model execution.

    Contains output location and scoring statistics returned by astore.score action.
    Used for chaining models (e.g., Astore → Explain workflow).

    Attributes:
        output_caslib: Output CAS library name where results are stored
        output_table: Output CAS table name containing scored data
        rows_scored: Number of rows successfully scored
        cas_table: Optional CASTable reference for direct data access

    Examples:
        >>> # Basic payload from Executor
        >>> payload = AstorePayload(
        ...     output_caslib="public",
        ...     output_table="scored_customers",
        ...     rows_scored=5000,
        ...     cas_table=None
        ... )
        >>> print(f"Scored {payload.rows_scored} rows")

        >>> # With CASTable reference
        >>> payload_with_table = AstorePayload(
        ...     output_caslib="public",
        ...     output_table="scored_data",
        ...     rows_scored=1000,
        ...     cas_table=connection.CASTable("scored_data", caslib="public")
        ... )
    """

    output_caslib: str
    output_table: str
    rows_scored: int
    cas_table: CASTable | None = None


@dataclass(frozen=True)
class ExplainPayload:
    """Payload from Explain model execution.

    Contains Shapley values and optional output location returned by
    explainModel.shapleyExplainer action.

    Attributes:
        shapley_values: List of Shapley value records, each containing
                       variable names and their Shapley contributions
        output_caslib: Optional output CAS library (if results were saved)
        output_table: Optional output table name (if results were saved)

    Examples:
        >>> # Shapley values for one observation
        >>> payload = ExplainPayload(
        ...     shapley_values=[
        ...         {"Variable": "age", "ShapleyValue": 0.15},
        ...         {"Variable": "income", "ShapleyValue": 0.32},
        ...         {"Variable": "tenure", "ShapleyValue": -0.08},
        ...     ],
        ...     output_caslib=None,
        ...     output_table=None
        ... )
        >>> for row in payload.shapley_values:
        ...     print(f"{row['Variable']}: {row['ShapleyValue']}")

        >>> # With saved output location
        >>> payload_saved = ExplainPayload(
        ...     shapley_values=[...],
        ...     output_caslib="explain_results",
        ...     output_table="customer_123_shapley"
        ... )
    """

    shapley_values: list[ShapleyValues]
    output_caslib: str | None = None
    output_table: str | None = None


@dataclass(frozen=True)
class DataStepPayload:
    """Payload from DataStep execution.

    Contains execution status and output location returned by datastep.runCode action.
    Used for custom preprocessing before model scoring.

    Attributes:
        success: Whether DATA step executed successfully
        message: Execution message or status description
        output_caslib: Output CAS library name (parsed from code or explicit)
        output_table: Output table name (parsed from code or explicit)

    Examples:
        >>> # Successful execution
        >>> payload = DataStepPayload(
        ...     success=True,
        ...     message="DataStep executed successfully",
        ...     output_caslib="public",
        ...     output_table="preprocessed_data"
        ... )
        >>> if payload.success:
        ...     print(f"Output: {payload.output_caslib}.{payload.output_table}")

        >>> # With execution details
        >>> payload_detailed = DataStepPayload(
        ...     success=True,
        ...     message="Processed 10000 rows, created 3 new variables",
        ...     output_caslib="work",
        ...     output_table="temp_result"
        ... )
    """

    success: bool
    message: str
    output_caslib: str
    output_table: str
