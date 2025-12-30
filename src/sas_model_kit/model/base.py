"""Base model class for synchronous model execution.

This module defines the abstract base class for all synchronous models,
establishing the execute() interface for model operations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sas_model_kit.operation import OperationProtocol
    from sas_model_kit.parameter import BaseModelParameter
    from sas_model_kit.result import ModelResult


class SyncModel(ABC):
    """Abstract base class for synchronous model execution.

    Provides the foundational interface for executing models against
    SAS operations. All concrete model implementations must extend
    this class and implement the execute() method.

    The name SyncModel distinguishes it from pydantic.BaseModel and
    clearly indicates synchronous execution semantics.

    Examples:
        >>> class MyModel(SyncModel):
        ...     def execute(
        ...         self,
        ...         operation: OperationProtocol,
        ...         parameter: BaseModelParameter,
        ...     ) -> ModelResult:
        ...         # Implementation
        ...         pass
    """

    @abstractmethod
    def execute(
        self,
        operation: OperationProtocol,
        parameter: BaseModelParameter,
    ) -> ModelResult:
        """Execute the model with given operation and parameters.

        Args:
            operation: The operation protocol for SAS interaction
            parameter: The model execution parameters

        Returns:
            ModelResult containing execution status and data

        Raises:
            RuntimeError: If execution fails
            ValueError: If parameters are invalid

        Note:
            Concrete implementations should:
            1. Validate parameters using parameter.validate()
            2. Perform necessary operation checks (table_exists, etc.)
            3. Execute the model operation
            4. Return ModelResult with appropriate status

        Examples:
            >>> model = MyModel()
            >>> result = model.execute(operation, parameter)
            >>> if result.is_success:
            ...     process(result.data)
        """
        ...
