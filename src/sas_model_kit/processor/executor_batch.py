"""Batch Operation Executor.

Encapsulates common batch-oriented CAS operations used by processors,
keeping processors focused on orchestration logic.

Responsibilities (CSRP):
    - Upload DataFrame to CAS
    - Concatenate temporary tables into final output
    - Cleanup temporary tables
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Generic, Protocol, TypeVar

from sas_model_kit.datasource.base import DataSourceProtocol
from sas_model_kit.operation import OperationProtocol


class TableT(Protocol):
    caslib: str
    name: str


DataFrameT = TypeVar(
    "DataFrameT"
)  # Operation input type (DataFrame, SASDataFrame, etc.)
ReturnT = TypeVar("ReturnT")  # Generic return type for operations


class BatchOperationExecutor(Generic[DataFrameT, ReturnT]):
    """Executor for common batch operations over OperationProtocol."""

    def __init__(self, operation: OperationProtocol[DataFrameT, ReturnT]) -> None:
        self.operation = operation

    def upload_dataframe(self, datasource: DataSourceProtocol[DataFrameT]) -> None:
        """Upload a SASDataFrame to CAS."""
        return datasource.prepare(self.operation)

    def concat_tables(
        self,
        inputs: Sequence[TableT],
        *,
        caslib: str,
        output_table: str,
        replace: bool = True,
    ) -> TableT:
        """Concatenate input tables into a single output table."""
        return self.operation.call_action(
            "table.concat",
            casout={"name": output_table, "caslib": caslib, "replace": replace},
            inputs=inputs,
        )

    def cleanup_tables(self, temp_tables: Sequence[TableT]) -> None:
        """Drop temporary tables created during batch processing."""
        for temp_table in temp_tables:
            self.operation.drop_table(caslib=temp_table.caslib, table=temp_table.name)
