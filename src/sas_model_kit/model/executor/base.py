"""Executor base interfaces.

Defines abstract executor contract for converting parameters and executing
backend operations to produce domain payloads. Executors are SRP-focused:
map parameter -> call backend -> parse payload.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from sas_model_kit.operation import OperationProtocol
from sas_model_kit.parameter import BaseModelParameter

P = TypeVar("P", bound=BaseModelParameter)
R_co = TypeVar("R_co", covariant=True)


class ModelExecutor(ABC, Generic[P, R_co]):
    """Abstract executor contract.

    Executors encapsulate backend-specific execution details and return
    pure payload data. Error handling and result wrapping are the Model
    layer's responsibility.
    """

    @abstractmethod
    def execute(
        self,
        operation: OperationProtocol,
        parameter: P,
        **context: Any,
    ) -> R_co:
        """Execute backend action and return payload."""
        ...
