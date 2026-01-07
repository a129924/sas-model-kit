"""AstoreModel - Single-row ASTORE scoring model.

This module provides the AstoreModel for executing ASTORE binary model
scoring operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from typing_extensions import override

from sas_model_kit.model.executor import ModelExecutor
from sas_model_kit.model.payloads import AstorePayload
from sas_model_kit.model.sync_model import SyncModel
from sas_model_kit.operation import OperationProtocol
from sas_model_kit.parameter import AstoreParameter
from sas_model_kit.result import (
    Err,
    ExecutionMetadata,
    ModelError,
    ModelSuccess,
    Ok,
    Result,
)


@dataclass(frozen=True)
class AstoreModel(SyncModel[AstoreParameter, AstorePayload]):
    """ASTORE model for binary model scoring.

    Executes astore.score action to score input data using a pre-compiled
    ASTORE binary model. Returns output location and row count.

    ⚠️ Single execution:
        - Scores all rows in input table
        - Returns AstorePayload with output location
        - For preprocessing workflows: output can feed into ExplainModel

    Attributes:
        executor: ModelExecutor for Astore operations

    Examples:
        >>> from sas_model_kit.model.executor import SwatAstoreExecutor
        >>> executor = SwatAstoreExecutor()
        >>> model = AstoreModel(executor=executor)
        >>>
        >>> result = model.execute(operation, astore_param)
        >>> if result.is_ok:
        ...     payload = result.unwrap().data
        ...     print(f"Scored {payload.rows_scored} rows")
        ...     print(f"Output: {payload.output_caslib}.{payload.output_table}")
    """

    executor: ModelExecutor[AstoreParameter, AstorePayload]

    @override
    def execute(
        self,
        operation: OperationProtocol,
        parameter: AstoreParameter,
        **context: Any,
    ) -> Result[ModelSuccess[AstorePayload], ModelError]:
        """Execute ASTORE scoring.

        Flow:
            1. Validate parameter
            2. Execute via executor → AstorePayload
            3. Wrap in ModelSuccess
            4. Return Ok/Err

        Args:
            operation: OperationProtocol for SWAT action calls
            parameter: AstoreParameter with input/model/output config
            **context: Execution context (optional overrides)

        Returns:
            Result[ModelSuccess[AstorePayload], ModelError]:
                - Ok: Contains AstorePayload with output location, rows_scored
                - Err: Contains ModelError with message and cause

        Examples:
            >>> result = astore_model.execute(operation, param)
            >>> if result.is_ok:
            ...     payload = result.unwrap().data
            ...     # Use output for downstream tasks
            ...     explain_param.train_table = payload.output_table
        """
        try:
            # Execute via executor
            payload = self.executor.execute(operation, parameter, **context)

            # Wrap in ModelSuccess
            # Extract execution time from context (set by executor)
            execution_time_ms = context.get("execution_time_ms", 0.0)
            success = ModelSuccess(
                data=payload,
                metadata=ExecutionMetadata(
                    execution_time_ms=execution_time_ms,
                    rows_affected=payload.rows_scored,
                ),
            )
            return Ok(success)

        except Exception as e:
            # Convert to ModelError
            error = ModelError(
                message=f"ASTORE model execution failed: {str(e)}",
                metadata=ExecutionMetadata(
                    execution_time_ms=context.get("execution_time_ms", 0.0),
                    rows_affected=0,
                ),
                cause=e,
            )
            return Err(error)
