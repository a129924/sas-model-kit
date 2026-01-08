"""ExplainModel - Single-row explainability model.

This module provides the ExplainModel for executing Shapley value
explanations on a single observation.

⚠️ Single-row execution:
    - SWAT's explainModel.shapleyExplainer WHERE clause handles ONE row only
    - For batch processing, use BatchExplainProcessor
    - Application layer loops over IDs: for id in ids: model.execute(...)

Architecture (CSRP - Concrete Single Responsibility Principle):
    - Concrete class (not dataclass) implementing SyncModel protocol
    - Final executor: injected via __init__, cannot be changed
    - @override decorators on all SyncModel implementations
"""

from __future__ import annotations

from typing import Any, Final

from typing_extensions import override

from sas_model_kit.model.executor import ModelExecutor
from sas_model_kit.model.payloads import ExplainPayload
from sas_model_kit.model.sync_model import SyncModel
from sas_model_kit.operation import OperationProtocol
from sas_model_kit.parameter import ExplainParameter
from sas_model_kit.result import (
    Err,
    ExecutionMetadata,
    ModelError,
    ModelSuccess,
    Ok,
    Result,
)


class ExplainModel(SyncModel[ExplainParameter, ExplainPayload]):
    """Single-row explainability model using Shapley values.

    Executes explainModel.shapleyExplainer for ONE observation at a time.
    Wraps Executor execution with Result[ModelSuccess, ModelError].

    Design (CSRP):
        - Concrete class (not dataclass)
        - Final executor: dependency injection via __init__
        - All methods explicitly override SyncModel abstract methods

    ⚠️ Important:
        - This is SINGLE-ROW execution
        - SWAT explainModel.shapleyExplainer WHERE handles one row only
        - Application layer must loop: for id in ids: model.execute(...)
        - For batch: use BatchExplainProcessor

    Attributes:
        executor: ModelExecutor[ExplainParameter, ExplainPayload] (Final)
                 Cannot be changed after initialization

    Examples:
        >>> from sas_model_kit.model.executor import SwatExplainExecutor
        >>> executor = SwatExplainExecutor()
        >>> model = ExplainModel(executor=executor)
        >>>
        >>> # Single execution
        >>> result = model.execute(
        ...     operation,
        ...     parameter,
        ...     where_condition="customer_id='123'"
        ... )
        >>> if result.is_ok:
        ...     shapley_values = result.unwrap().data.shapley_values
    """

    def __init__(
        self,
        executor: ModelExecutor[ExplainParameter, ExplainPayload],
    ) -> None:
        """Initialize ExplainModel with executor dependency.

        Args:
            executor: ModelExecutor for Explain operations (Final)

        Examples:
            >>> executor = SwatExplainExecutor()
            >>> model = ExplainModel(executor=executor)
        """
        object.__setattr__(self, "_executor", executor)

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent attribute modification after initialization (immutable)."""
        raise AttributeError(
            f"Cannot modify {self.__class__.__name__}.{name} - instance is immutable"
        )

    @property
    def executor(self) -> ModelExecutor[ExplainParameter, ExplainPayload]:
        """Access the executor (read-only)."""
        return object.__getattribute__(self, "_executor")

    @override
    def execute(
        self,
        operation: OperationProtocol,
        parameter: ExplainParameter,
        **context: Any,
    ) -> Result[ModelSuccess[ExplainPayload], ModelError]:
        """Execute single-row Explain model.

        Flow:
            1. Validate parameter (delegate to parameter.validate())
            2. Execute via executor → ExplainPayload
            3. Wrap in ModelSuccess with metadata
            4. Return Ok(success) or Err(error)

        Args:
            operation: OperationProtocol for SWAT action calls
            parameter: ExplainParameter with model/training config
            **context: Execution context (where_condition, output locations)

        Returns:
            Result[ModelSuccess[ExplainPayload], ModelError]:
                - Ok: Contains ExplainPayload with shapley_values
                - Err: Contains ModelError with message and cause

        Examples:
            >>> result = explain_model.execute(
            ...     operation,
            ...     explain_param,
            ...     where_condition="id='customer_123'",
            ...     output_caslib="explain_output",
            ...     output_table="shapley_customer_123"
            ... )
            >>> if result.is_ok:
            ...     payload = result.unwrap().data
            ...     for row in payload.shapley_values:
            ...         print(f"{row['Variable']}: {row['ShapleyValue']}")
        """
        try:
            # Execute via executor (validation happens inside)
            payload = self.executor.execute(operation, parameter, **context)

            # Wrap in ModelSuccess
            success = ModelSuccess(
                data=payload,
                metadata=ExecutionMetadata(
                    execution_time_ms=0.0,
                    rows_affected=len(payload.shapley_values),
                ),
            )
            return Ok(success)

        except Exception as e:
            # Convert any exception to ModelError
            error = ModelError(
                message=f"Explain model execution failed: {str(e)}",
                metadata=ExecutionMetadata(
                    execution_time_ms=0.0,
                    rows_affected=0,
                ),
                cause=e,
            )
            return Err(error)
