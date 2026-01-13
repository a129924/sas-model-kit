"""
SWAT-specific operation adapter implementation.

This module implements OperationProtocol for SWAT (SAS Scripting Wrapper
for Analytics Transfer), adapting SWAT's CAS session API to our protocol.
"""

from typing import Any, NamedTuple

import swat
from pandas import DataFrame
from typing_extensions import override

from sas_model_kit.error import OperationError
from sas_model_kit.operation.base import BaseOperation
from sas_model_kit.result import Err, Ok, Result


class ActionSetName(NamedTuple):
    """Helper named tuple for actionset and action names."""

    actionset: str
    action: str


class SWATOperationAdapter(
    BaseOperation[swat.CAS, DataFrame | swat.SASDataFrame, swat.CASTable]
):
    """
    SWAT-specific operation adapter (CSRP).

    Implements OperationProtocol using SWAT's CAS session API, following CSRP
    (Concrete Single Responsibility Principle).

    Automatically loads required actionsets on first use for transparent operation.
    Each actionset is loaded only once per adapter instance.

    Attributes:
        _session: Underlying SWAT CAS session
        _loaded_actionsets: Set of actionsets already loaded in this instance

    Thread Safety:
        Not thread-safe. If using in ThreadPool, create separate adapter
        instances for each thread.

    Generic Types:
        - swat.CAS: Connection type
        - DataFrame | swat.SASDataFrame: Input data type (ReSourceType)
        - swat.CASTable: Return type from upload_data (ReturnType)

    Example:
        >>> connection = SWATConnection(...)
        >>> operation = connection.get_operation()
        >>> # Actionset 'astore' auto-loaded on first call
        >>> result = operation.call_action('astore.score', ...)
        >>> # Subsequent calls reuse loaded actionset
        >>> result2 = operation.call_action('astore.score', ...)
        >>> # upload_data now returns CASTable
        >>> cas_table = operation.upload_data(df, caslib='public', table='data')
    """

    def __init__(self, connection: swat.CAS) -> None:
        """Initialize SWAT operation adapter with actionset tracking.

        Args:
            connection: SWAT CAS session
        """
        super().__init__(connection)
        self._loaded_actionsets: set[str] = set()  # set[swat.ActionSetName: str]

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
    def call_action(
        self, action_name: str, **kwargs: Any
    ) -> Result[Any, OperationError]:
        """
        Execute a SAS action using SWAT with automatic actionset loading.

        Uses SWAT's __getattr__ pattern to dynamically invoke actions:
        - 'astore.score' -> session.astore.score(**kwargs)
        - 'explainModel.explain' -> session.explainModel.explain(**kwargs)

        Automatically loads the required actionset if not already loaded.
        Each actionset is loaded only once per adapter instance.

        Args:
            action_name: Action to execute (format: 'actionset.action')
            **kwargs: Action-specific parameters

        Returns:
            SWAT CASResults object containing action results

        Raises:
            ValueError: If action_name format is invalid
            RuntimeError: If action execution fails

        Example:
            >>> # First call auto-loads 'astore' actionset
            >>> result = adapter.call_action(
            ...     'astore.score',
            ...     table={'name': 'input_data'},
            ...     rstore={'name': 'my_model'}
            ... )
            >>> # Subsequent calls reuse loaded actionset
            >>> result2 = adapter.call_action('astore.score', ...)
        """
        if "." not in action_name:
            return Err(
                OperationError(
                    code="INVALID_ACTION_NAME",
                    message=(
                        f"Invalid action_name format: '{action_name}'. "
                        "Expected 'actionset.action' (e.g., 'astore.score')"
                    ),
                    context={"action_name": action_name},
                )
            )

        actionset_name, action_method = self._parse_action_name(action_name)
        self._ensure_actionset_loaded(actionset_name)

        try:
            actionset = getattr(self._session, actionset_name)
            action = getattr(actionset, action_method)
            return Ok(action(**kwargs))
        except AttributeError as exc:
            return Err(
                OperationError(
                    code="ACTION_NOT_FOUND",
                    message=(
                        f"Action '{action_name}' not found in SWAT session. "
                        f"Original error: {exc}"
                    ),
                    cause=exc,
                    context={"action_name": action_name},
                )
            )
        except Exception as exc:
            return Err(
                OperationError(
                    code="UNEXPECTED_EXCEPTION",
                    message=f"Failed to execute action '{action_name}': {exc}",
                    cause=exc,
                    context={
                        "action_name": action_name,
                        "exception_type": type(exc).__name__,
                    },
                )
            )

    def _parse_action_name(self, action_name: str) -> ActionSetName:
        """Parse action_name into ActionSetName named tuple.

        Args:
            action_name: Action name in 'actionset.action' format

        Returns:
            ActionSetName named tuple with actionset and action attributes
        """

        parts = action_name.split(".", 1)

        return ActionSetName(actionset=parts[0], action=parts[1])

    def _ensure_actionset_loaded(self, actionset_name: str) -> None:
        """Ensure actionset is loaded, loading it if necessary.

        Loads actionset only once per adapter instance. Tracks loaded
        actionsets in _loaded_actionsets set.

        Args:
            actionset_name: Name of actionset to ensure is loaded

        Note:
            This method is idempotent - safe to call multiple times.
        """
        # Skip if already loaded in this instance
        if actionset_name in self._loaded_actionsets:
            return

        # Check if actionset is loaded on server
        # Note: has_actionset() is a SWAT CAS session method
        if hasattr(self._session, "has_actionset") and self._session.has_actionset(
            actionset_name
        ):
            # Already loaded on server; mark as loaded in this instance
            self._loaded_actionsets.add(actionset_name)
            return

        # Load actionset on server if not already loaded or has_actionset is unavailable
        try:
            self._session.loadactionset(actionset_name)
        except Exception as e:
            from warnings import warn

            warn(
                f"Warning: Failed to load actionset '{actionset_name}': {e}",
                stacklevel=2,
            )

        # Mark as loaded in this instance regardless of success/failure
        # This prevents repeated load attempts for unavailable actionsets
        self._loaded_actionsets.add(actionset_name)

    @override
    def upload_data(
        self,
        data: DataFrame | swat.SASDataFrame,
        caslib: str,
        table: str,
    ) -> Result[swat.CASTable, OperationError]:
        """
        Upload data to CAS using SWAT and return CASTable reference.

        Uses swat.CAS.upload_frame() for DataFrame uploads. Supports pandas
        DataFrames natively via SWAT's conversion.

        Args:
            data: Data to upload (currently supports pandas DataFrame)
            caslib: Target CAS library
            table: Target table name

        Returns:
            swat.CASTable: Reference to uploaded table in CAS

        Raises:
            TypeError: If data format is unsupported
            RuntimeError: If upload fails

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
            >>> cas_table = adapter.upload_data(df, caslib='public', table='my_data')
            >>> print(cas_table.name)
            'my_data'
        """
        try:
            self._session.upload_frame(
                data,
                casout={
                    "name": table,
                    "caslib": caslib,
                    "replace": True,
                },
            )

            return Ok(self._session.CASTable(name=table, caslib=caslib))

        except Exception as exc:
            return Err(
                OperationError(
                    code="UPLOAD_FAILED",
                    message=f"Failed to upload data to {caslib}.{table}: {exc}",
                    cause=exc,
                    context={
                        "caslib": caslib,
                        "table": table,
                        "data_type": type(data).__name__,
                        "exception_type": type(exc).__name__,
                    },
                )
            )

    @override
    def table_exists(self, caslib: str, table: str) -> Result[bool, OperationError]:
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

    @override
    def drop_table(self, caslib: str, table: str) -> None:
        """
        Drop a table from the specified CAS library.

        Uses SWAT's table.dropTable action to remove the specified table.

        Args:
            caslib: CAS library name
            table: Table name to drop

        Returns:
            None

        Example:
            >>> adapter.drop_table('public', 'my_data')
        """
        try:
            self._session.table.dropTable(
                caslib=caslib,
                name=table,
                quiet=True,  # Suppress errors if table doesn't exist
            )
        except Exception as e:
            raise RuntimeError(f"Failed to drop table {caslib}.{table}: {e}") from e
