"""
DataSource layer for SAS Model Kit.

This module provides data source protocols and implementations for
preparing input data and fetching execution results, following
PyTorch's Dataset pattern.
"""

from sas_model_kit.datasource.base import DataSourceProtocol
from sas_model_kit.datasource.cas_table import CASTableDataSource
from sas_model_kit.datasource.dataframe import DataFrameDataSource
from sas_model_kit.datasource.json import JSONDataSource

__all__ = [
    "DataSourceProtocol",
    "DataFrameDataSource",
    "CASTableDataSource",
    "JSONDataSource",
]
