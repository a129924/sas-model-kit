"""
SAS Model Kit - Python package for SAS Viya Analytics Models.

This package provides a clean, Pythonic API for working with SAS Viya
analytics models (ASTORE, Explainable AI, Data Step).

Modules:
    connection: Connection management (SessionProtocol, SWATConnection)
    operation: Action execution (OperationProtocol, SWATOperationAdapter)
    datasource: Data handling (DataSourceProtocol, DataFrameDataSource, etc.)

Example:
    >>> from sas_model_kit.connection.swat import SWATConnection
    >>> from sas_model_kit.datasource import DataFrameDataSource
    >>>
    >>> # Connect to CAS
    >>> with SWATConnection('host', 5570) as conn:
    ...     operation = conn.get_operation()
    ...     # Use operation to execute models
"""

__version__ = "0.2.0"

__all__ = [
    "__version__",
]
