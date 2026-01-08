"""DataStepModel - DATA step execution model.

This module provides the DataStepModel for executing custom SAS DATA step
code for preprocessing or data transformation tasks.

Architecture (CSRP):
    - Concrete class (not dataclass) implementing SyncModel protocol
    - Final executor: injected via __init__, cannot be changed
    - @override decorators on all SyncModel implementations
"""

from __future__ import annotations

from typing import Any, Final

from typing_extensions import override

from sas_model_kit.model.executor import ModelExecutor
from sas_model_kit.model.payloads import DataStepPayload
from sas_model_kit.model.sync_model import SyncModel
from sas_model_kit.operation import OperationProtocol
from sas_model_kit.parameter import DataStepParameter
from sas_model_kit.result import (
    Err,
    ExecutionMetadata,
    ModelError,
    ModelSuccess,
    Ok,
    Result,
)


class DataStepModel(SyncModel[DataStepParameter, DataStepPayload]):
    """DATA step execution model.

    Executes custom SAS DATA step code via datastep.runCode action.
    Useful for preprocessing, data transformation, or custom logic.

    Design (CSRP):
        - Concrete class (not dataclass)
        - Final executor: dependency injection via __init__
        - All methods explicitly override SyncModel abstract methods

    ⚠️ Single execution:
        - Runs complete DATA step code once
        - Returns success status and output location
        - Output can feed into downstream models (Astore, Explain)

    Attributes:
        executor: ModelExecutor[DataStepParameter, DataStepPayload] (Final)
                 Cannot be changed after initialization

    Examples:
        >>> from sas_model_kit.model.executor import SwatDataStepExecutor
        >>> executor = SwatDataStepExecutor()
        >>> model = DataStepModel(executor=executor)
        >>>
        >>> result = model.execute(operation, datastep_param)
        >>> if result.is_ok:
        ...     payload = result.unwrap().data
        ...     if payload.success:
        ...         print(f"Output: {payload.output_caslib}.{payload.output_table}")
    """

    def __init__(
        self,
        executor: ModelExecutor[DataStepParameter, DataStepPayload],
    ) -> None:
        """Initialize DataStepModel with executor dependency.

        Args:
            executor: ModelExecutor for DataStep operations (Final)

        Examples:
            >>> executor = SwatDataStepExecutor()
            >>> model = DataStepModel(executor=executor)
        """
        object.__setattr__(self, "_executor", executor)

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent attribute modification after initialization (immutable)."""
        raise AttributeError(
            f"Cannot modify {self.__class__.__name__}.{name} - instance is immutable"
        )

    @property
    def executor(self) -> ModelExecutor[DataStepParameter, DataStepPayload]:
        """Access the executor (read-only)."""
        return object.__getattribute__(self, "_executor")

    @override
    def execute(
        self,
        operation: OperationProtocol,
        parameter: DataStepParameter,
        **context: Any,
    ) -> Result[ModelSuccess[DataStepPayload], ModelError]:
        """Execute DATA step code.

        Flow:
            1. Validate parameter (code, output location)
            2. Execute via executor → DataStepPayload
            3. Wrap in ModelSuccess
            4. Return Ok/Err

        Args:
            operation: OperationProtocol for SWAT action calls
            parameter: DataStepParameter with code and output config
            **context: Execution context (optional)

        Returns:
            Result[ModelSuccess[DataStepPayload], ModelError]:
                - Ok: Contains DataStepPayload with success status, message
                - Err: Contains ModelError with message and cause

        Examples:
            >>> result = datastep_model.execute(operation, param)
            >>> if result.is_ok:
            ...     payload = result.unwrap().data
            ...     if not payload.success:
            ...         print(f"Warning: {payload.message}")
        """
        try:
            # Execute via executor
            payload = self.executor.execute(operation, parameter, **context)

            # Wrap in ModelSuccess
            success = ModelSuccess(
                data=payload,
                # TODO: 要看 要不要加上時間
                metadata=ExecutionMetadata(
                    execution_time_ms=0.0,
                    rows_affected=0,
                ),
            )
            return Ok(success)

        except Exception as e:
            # Convert to ModelError
            error = ModelError(
                message=f"DATA step execution failed: {str(e)}",
                # TODO: 要看 要不要加上時間
                metadata=ExecutionMetadata(
                    execution_time_ms=0.0,
                    rows_affected=0,
                ),
                cause=e,
            )
            return Err(error)
