"""
SWAT-specific operation adapter implementation.

This module implements OperationProtocol for SWAT (SAS Scripting Wrapper
for Analytics Transfer), adapting SWAT's CAS session API to our protocol.
"""

from typing import Any

import swat
from pandas import DataFrame
from typing_extensions import override

from sas_model_kit.operation.base import BaseOperation


class SWATOperationAdapter(BaseOperation[swat.CAS, DataFrame]):
    """
    SWAT-specific operation adapter.

    Implements OperationProtocol using SWAT's CAS session API, following CSRP
    (Concrete Single Responsibility Principle).

    Attributes:
        _session: Underlying SWAT CAS session

    Example:
        >>> connection = SWATConnection(...)
        >>> operation = connection.get_operation()
        >>> result = operation.call_action('astore.score', ...)
    """

    @override
    def _check_connection_type(self, connection: Any) -> None:
        if not connection:
            raise ValueError("Connection cannot be None")
        if not isinstance(connection, swat.CAS):
            raise TypeError(
                f"SWATOperationAdapter requires a swat.CAS connection, "
                f"got {type(connection).__name__}"
            )

    @override
    def call_action(self, action_name: str, **kwargs: Any) -> Any:
        """
        Execute a SAS action using SWAT.

        Uses SWAT's __getattr__ pattern to dynamically invoke actions:
        - 'astore.score' -> session.astore.score(**kwargs)
        - 'explainModel.explain' -> session.explainModel.explain(**kwargs)

        Args:
            action_name: Action to execute (format: 'actionset.action')
            **kwargs: Action-specific parameters

        Returns:
            SWAT CASResults object containing action results

        Raises:
            ValueError: If action_name format is invalid
            RuntimeError: If action execution fails

        Example:
            >>> result = adapter.call_action(
            ...     'astore.score',
            ...     table={'name': 'input_data'},
            ...     rstore={'name': 'my_model'}
            ... )
        """
        # Validate action_name format
        if "." not in action_name:
            raise ValueError(
                f"Invalid action_name format: '{action_name}'. "
                f"Expected 'actionset.action' (e.g., 'astore.score')"
            )

        # Parse actionset and action
        parts = action_name.split(".", 1)
        actionset_name = parts[0]
        action_method = parts[1]

        try:
            # Use SWAT's __getattr__ pattern to access actionset
            actionset = getattr(self._session, actionset_name)
            action = getattr(actionset, action_method)

            # Execute action
            return action(**kwargs)

        except AttributeError as e:
            raise ValueError(
                f"Action '{action_name}' not found in SWAT session. Original error: {e}"
            ) from e

        except Exception as e:
            raise RuntimeError(f"Failed to execute action '{action_name}': {e}") from e

    @override
    def upload_data(self, data: DataFrame, caslib: str, table: str) -> None:
        """
        Upload data to CAS using SWAT.

        Uses swat.CAS.upload_frame() for DataFrame uploads. Supports pandas
        DataFrames natively via SWAT's conversion.

        Args:
            data: Data to upload (currently supports pandas DataFrame)
            caslib: Target CAS library
            table: Target table name

        Raises:
            TypeError: If data format is unsupported
            RuntimeError: If upload fails

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
            >>> adapter.upload_data(df, caslib='public', table='my_data')
        """
        try:
            # SWAT's upload_frame accepts pandas DataFrame
            # Will auto-convert or raise TypeError if unsupported
            self._session.upload_frame(
                data,
                casout={
                    "name": table,
                    "caslib": caslib,
                    "replace": True,  # Always replace for idempotency
                },
            )

        except TypeError as e:
            raise TypeError(
                f"Unsupported data type for upload: {type(data).__name__}. "
                f"SWAT supports pandas DataFrame. Original error: {e}"
            ) from e

        except Exception as e:
            raise RuntimeError(f"Failed to upload data to {caslib}.{table}: {e}") from e

    @override
    def table_exists(self, caslib: str, table: str) -> bool:
        """
        Check if a table exists in the specified CAS library.

        Uses SWAT's table.tableExists action to verify table presence.

        Args:
            caslib: CAS library name
            table: Table name to check

        Returns:
            True if table exists, False otherwise

        Example:
            >>> if adapter.table_exists('public', 'my_data'):
            ...     print("Table exists")
        """
        try:
            result = self._session.table.tableExists(  # CASResults
                caslib=caslib,
                name=table,
            )
            # CASResults['exists'] => 0 || 2

            # SWAT returns CASResults with 'exists' key
            return bool(result.get("exists", 0))

        except Exception:
            # If action fails, assume table doesn't exist
            return False

    @override
    def model_exists(self, caslib: str, table: str) -> bool:
        """
        Check if a model (ASTORE) exists in the specified CAS library.

        Uses SWAT's table.tableExists action since ASTORE models are
        stored as CAS tables.

        Args:
            caslib: CAS library name containing models
            table: Model table name (ASTORE) to check

        Returns:
            True if model exists, False otherwise

        Example:
            >>> if adapter.model_exists('models', 'my_astore'):
            ...     print("Model exists")
        """
        # ASTORE models are CAS tables, so we can reuse table_exists
        return self.table_exists(caslib, table)
