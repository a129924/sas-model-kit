"""Synchronous model base class with typed execution interface.

This module provides the SyncModel abstract base class for single-row
execution models. Models in this layer coordinate parameter validation,
executor delegation, and result wrapping.

⚠️ Pure Transform Principle Applied:
    - Parameter layer: Validates input (type, required, business rules)
    - Model layer: Only executes (assumes valid input from Parameter)
    - Executor: May throw exceptions internally (caught as ModelError)
    - Validation is CALLER'S responsibility, not Model's

⚠️ Single-Row Execution Semantics:
    - One Parameter → One Payload
    - No batch processing logic (see BatchProcessor layer)
    - No ID alignment logic (see Application layer)

Design:
    - Generic[ParameterT, PayloadT] for type safety
    - ABC with @abstractmethod execute()
    - Returns Result[ModelSuccess[PayloadT], ModelError]
    - Immutable: @dataclass(frozen=True)
    - Executor exceptions are caught and wrapped as ModelError

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
    ...             # Parameter.validate() already called by caller
    ...             # Model only executes (Pure Transform)
    ...             payload = self.executor.execute(operation, parameter, **context)
    ...             return Ok(ModelSuccess(data=payload))
    ...         except Exception as e:
    ...             # Executor exceptions caught and wrapped
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

    Pure Transform Principle:
        - Parameter layer: Validates input (delegated to Parameter.validate())
        - Model layer: Only executes (assumes valid input)
        - Executor: May throw exceptions (caught as ModelError)
        - Validation is CALLER's responsibility, NOT Model's

    Single-Row Execution Semantics:
        - Processes one Parameter → returns one Payload
        - Does NOT handle batch processing (use BatchProcessor layer)
        - Does NOT handle ID alignment (use Application layer)

    Responsibilities:
        ✓ Call Parameter.validate() before execution (or assume caller did)
        ✓ Execute via Executor with validated parameter
        ✓ Wrap results as Result[ModelSuccess[PayloadT], ModelError]
        ✓ Catch Executor exceptions and convert to ModelError

    Exception Handling:
        - Executor internal errors → caught as exceptions
        - Exceptions wrapped as ModelError (line-level granularity)
        - NOT responsible for parameter validation errors (caller's job)

    Type Parameters:
        ParameterT: The parameter type (e.g., ExplainParameter)
        PayloadT: The payload type (e.g., ExplainPayload)

    Examples:
        >>> # Concrete implementation (Pure Transform)
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
        ...         try:
        ...             # Assume Parameter.validate() already called by caller
        ...             # Model only executes (Pure Transform, no validation)
        ...             payload = self.executor.execute(operation, parameter, **context)
        ...             return Ok(ModelSuccess(data=payload))
        ...         except Exception as e:
        ...             # Executor exceptions caught and wrapped
        ...             return Err(ModelError(message=str(e), cause=e))
    """

    @abstractmethod
    def execute(
        self,
        operation: OperationProtocol,
        parameter: ParameterT,
        **context: Any,
    ) -> Result[ModelSuccess[PayloadT], ModelError]:
        """Execute single-row model operation (Pure Transform).

        Pure Transform Contract:
            - Assumes parameter is VALID (validation is caller's responsibility)
            - Only executes core logic (mapping → operation call → result parsing)
            - Catches Executor exceptions and wraps as ModelError
            - Does NOT validate input (validation layer is Parameter)

        Args:
            operation: Operation protocol for SAS action execution
            parameter: Model parameters (MUST be pre-validated by caller)
            **context: Additional execution context (e.g., where_condition,
                      output_caslib, output_table)

        Returns:
            Result[ModelSuccess[PayloadT], ModelError]:
                - Ok(ModelSuccess(data=payload, metadata=...)) on success
                - Err(ModelError(message=..., cause=...)) on Executor exception

        Raises:
            Should NOT raise exceptions directly - catch and wrap in Err()

        Examples:
            >>> # Caller must pre-validate parameter
            >>> param = ExplainParameter(...)
            >>> param.validate()  # Caller's responsibility
            >>>
            >>> result = model.execute(operation, param)
            >>> if result.is_ok:
            ...     payload = result.unwrap().data
            ...     print(f"Success: {payload}")
            >>> else:
            ...     error = result.unwrap_err()
            ...     print(f"Executor failed: {error.message}")
        """
        ...
