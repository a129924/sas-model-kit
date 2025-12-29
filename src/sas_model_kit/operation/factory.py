"""
Operation factory for creating operation adapters.

This module provides the OperationFactory class that creates appropriate
OperationAdapter instances based on connection type, following the
Factory Method pattern.
"""

from sas_model_kit.connection.base import ConnectionType, SessionProtocol
from sas_model_kit.operation.base import OperationProtocol
from sas_model_kit.operation.swat import SWATOperationAdapter


class OperationFactory:
    """
    Factory for creating operation adapters from connections.

    Uses match/case pattern matching on connection_type to determine
    which OperationAdapter to instantiate. This avoids isinstance()
    checks and provides clean type-based dispatch.

    Example:
        >>> # Create operation from connection
        >>> connection = SWATConnection('host', 5570)
        >>> connection.connect()
        >>> operation = OperationFactory.create(connection)
        >>> result = operation.call_action('astore.score', ...)

        >>> # Works with any connection type
        >>> with SASCTLConnection(...) as conn:
        ...     operation = OperationFactory.create(conn)
        ...     # Use operation
    """

    @staticmethod
    def create(connection: SessionProtocol) -> OperationProtocol:
        """
        Create appropriate OperationAdapter for the given connection.

        Args:
            connection: SessionProtocol instance with connection_type attribute

        Returns:
            OperationProtocol implementation matching the connection type

        Raises:
            ValueError: If connection type is not supported
            ConnectionError: If connection is not healthy

        Example:
            >>> connection = SWATConnection('host', 5570)
            >>> connection.connect()
            >>> operation = OperationFactory.create(connection)
        """
        # Get session first to ensure connection is healthy
        session = connection.get_session()

        # Match on connection type to create appropriate adapter
        match connection.connection_type:
            case ConnectionType.SWAT:
                return SWATOperationAdapter(session)

            case ConnectionType.SASCTL:
                # Future implementation
                raise NotImplementedError(
                    "SASCTL operation adapter not yet implemented"
                )

            case ConnectionType.HTTPX:
                # Future implementation
                raise NotImplementedError("HTTPx operation adapter not yet implemented")

            case _:
                raise ValueError(
                    f"Unsupported connection type: {connection.connection_type}"
                )
