"""
Operation layer for SAS Model Kit.

This module provides operation protocols and adapters for executing
SAS actions across different backends (SWAT, SASCTL, HTTPx).
"""

from sas_model_kit.operation.base import OperationProtocol
from sas_model_kit.operation.factory import OperationFactory
from sas_model_kit.operation.swat import SWATOperationAdapter

__all__ = [
    "OperationProtocol",
    "OperationFactory",
    "SWATOperationAdapter",
]
