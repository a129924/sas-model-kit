"""CAS Table Transformer Protocol.

This module defines the abstract interface for all CAS table transformations.
Following CSRP (Concrete Single Responsibility Principle), each transformer
has a single, specific transformation responsibility.

Design Philosophy:
    - Dependency Injection: Operation injected at construction
    - Explicit Exceptions: Do not swallow exceptions, let them propagate
    - Lightweight: No ExecutionMetadata (that's for Model layer)
    - Single Responsibility: Each transformer does one thing well

Examples:
    >>> operation = connection.get_operation()
    >>> transformer = SortTransformer(operation, by=['age'])
    >>> try:
    ...     sorted_table = transformer.execute(input_table)
    ... except TransformationError as e:
    ...     logger.error(f"Sort failed: {e}")
"""

from abc import ABC, abstractmethod

try:
    from swat import CASTable
except ImportError as e:
    raise ImportError(
        "swat package is required for CASTableTransformer. "
        "Please install it via 'pip install swat'."
    ) from e

from sas_model_kit.error import OperationError, TransformationFailure
from sas_model_kit.result import Result

from ..operation.base import OperationProtocol


class CASTableTransformer(ABC):
    """Abstract base class for CAS table transformers.

    All CAS table transformation operations must inherit from this class
    and implement the execute() method. Follows CSRP: each concrete
    transformer has a single, specific transformation responsibility.

    Design Principles:
        - Constructor injection: Operation dependency injected at construction
        - Fail fast: Raise exceptions immediately, don't swallow them
        - No side effects: Execute() doesn't modify the input table (unless inplace)
        - Type-safe: Returns CASTable, not wrapped in Result (exceptions = errors)

    Attributes:
        operation: OperationProtocol instance for infrastructure operations

    Examples:
        >>> class MyTransformer(CASTableTransformer):
        ...     def execute(self, input_table: CASTable) -> CASTable:
        ...         # transformation logic
        ...         return transformed_table

        >>> operation = connection.get_operation()
        >>> transformer = MyTransformer(operation)
        >>> result = transformer.execute(table)
    """

    def __init__(self, operation: OperationProtocol) -> None:
        """Initialize transformer with operation dependency.

        Args:
            operation: Operation protocol instance providing infrastructure ops

        Examples:
            >>> operation = connection.get_operation()
            >>> transformer = SortTransformer(operation, by=['age'])
        """
        self.operation = operation

    @abstractmethod
    def execute(self, input_table: CASTable) -> Result[CASTable, TransformationFailure]:
        """Execute the transformation on the input table.

        This method must be implemented by all concrete transformers.
        It should perform a single, well-defined transformation and
        return the transformed CASTable wrapped in a Result.

        Design Contract:
            - Must not modify input_table unless explicitly documented
            - Returns Result[CASTable, semantic_error | OperationError]
            - Semantic errors: SortError, DuplicateKeyError (execution, not validation)
            - Must not validate input (validation is caller's responsibility)

        Args:
            input_table: The CAS table to transform

        Returns:
            Result containing a transformed CASTable or failure details.
        """
        ...
