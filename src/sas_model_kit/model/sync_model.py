"""Synchronous model base class with typed execution interface.

This module provides the SyncModel abstract base class for single-row
execution models. Models in this layer coordinate parameter validation,
executor delegation, and result wrapping.

⚠️ This is for SINGLE-ROW execution:
    - One Parameter → One Payload
    - No batch processing logic (see BatchProcessor layer)
    - No ID alignment logic (see Application layer)

Design:
    - Generic[ParameterT, PayloadT] for type safety
    - ABC with @abstractmethod execute()
    - Returns Result[ModelSuccess[PayloadT], ModelError]
    - Immutable: @dataclass(frozen=True)

Examples:
    >>> @dataclass(frozen=True)
    >>> class ExplainModel(SyncModel[ExplainParameter, ExplainPayload]):
    ...     executor: ModelExecutor[ExplainParameter, ExplainPayload]
    ...
    ...     @override
    ...     def execute(
    ...         self,
    ...         operation: OperationProtocol,
    ...         parameter: ExplainParameter,
    ...         **context: Any,
    ...     ) -> Result[ModelSuccess[ExplainPayload], ModelError]:
    ...         try:
    ...             payload = self.executor.execute(operation, parameter, **context)
    ...             return Ok(ModelSuccess(data=payload))
    ...         except Exception as e:
    ...             return Err(ModelError(message=str(e), cause=e))
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from sas_model_kit.operation import OperationProtocol
from sas_model_kit.parameter import BaseModelParameter
from sas_model_kit.result import ModelError, ModelSuccess, Result

# Type variables for generic model definition
ParameterT = TypeVar("ParameterT", bound=BaseModelParameter)
PayloadT = TypeVar("PayloadT")


@dataclass(frozen=True)
class SyncModel(ABC, Generic[ParameterT, PayloadT]):
    """Abstract base class for single-row synchronous model execution.

    ⚠️ Single-row execution semantics:
        - Processes one Parameter → returns one Payload
        - Does NOT handle batch processing (use BatchProcessor layer)
        - Does NOT handle ID alignment (use Application layer)

    Responsibilities:
        ✓ Validate parameters (delegate to Parameter.validate())
        ✓ Execute via Executor
        ✓ Wrap results as Result[ModelSuccess[PayloadT], ModelError]
        ✓ Handle exceptions and convert to ModelError

    Not responsible for:
        ✗ Batch processing coordination
        ✗ Multi-step workflows
        ✗ Data alignment or ID matching

    Type Parameters:
        ParameterT: The parameter type (e.g., ExplainParameter)
        PayloadT: The payload type (e.g., ExplainPayload)

    Examples:
        >>> # Concrete implementation
        >>> @dataclass(frozen=True)
        >>> class MyModel(SyncModel[MyParameter, MyPayload]):
        ...     executor: ModelExecutor[MyParameter, MyPayload]
        ...
        ...     @override
        ...     def execute(
        ...         self,
        ...         operation: OperationProtocol,
        ...         parameter: MyParameter,
        ...         **context: Any,
        ...     ) -> Result[ModelSuccess[MyPayload], ModelError]:
        ...         ...
    """

    @abstractmethod
    def execute(
        self,
        operation: OperationProtocol,
        parameter: ParameterT,
        **context: Any,
    ) -> Result[ModelSuccess[PayloadT], ModelError]:
        """Execute single-row model operation.

        Args:
            operation: Operation protocol for SAS action execution
            parameter: Model parameters (will be validated)
            **context: Additional execution context (e.g., where_condition,
                      output_caslib, output_table)

        Returns:
            Result[ModelSuccess[PayloadT], ModelError]:
                - Ok(ModelSuccess(data=payload, metadata=...)) on success
                - Err(ModelError(message=..., cause=...)) on failure

        Raises:
            Should NOT raise exceptions directly - catch and wrap in Err()

        Examples:
            >>> result = model.execute(operation, parameter)
            >>> if result.is_ok:
            ...     payload = result.unwrap().data
            ...     print(f"Success: {payload}")
            >>> else:
            ...     error = result.unwrap_err()
            ...     print(f"Error: {error.message}")
        """
        ...
