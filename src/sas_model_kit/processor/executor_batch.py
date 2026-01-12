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
    """Executor for common batch operations over OperationProtocol.

    Generic parameters:
        DataFrameT: Input data type (DataFrame, SASDataFrame, etc.)
        ReturnT: Return type from operation.upload_data() (CASTable, SparkTable, etc.)

    Design principle:
        Uses ReturnT for table operations to maintain type consistency with
        operation's return type. ReturnT should satisfy TableT protocol
        (having caslib and name attributes).
    """

    def __init__(self, operation: OperationProtocol[DataFrameT, ReturnT]) -> None:
        self.operation = operation

    def upload_dataframe(self, datasource: DataSourceProtocol[DataFrameT]) -> None:
        """Upload data via DataSource (optional integration layer)."""
        return datasource.prepare(self.operation)

    def concat_tables(
        self,
        inputs: Sequence[ReturnT],
        *,
        caslib: str,
        output_table: str,
        replace: bool = True,
    ) -> ReturnT:
        """Concatenate input tables into a single output table.

        Args:
            inputs: List of table references (same type as operation returns)
            caslib: CAS library for output table
            output_table: Output table name
            replace: Whether to replace existing table

        Returns:
            Concatenated table (same type as inputs)
        """
        return self.operation.call_action(
            "table.concat",
            casout={"name": output_table, "caslib": caslib, "replace": replace},
            inputs=inputs,
        )

    def cleanup_tables(self, temp_tables: Sequence[ReturnT]) -> None:
        """Drop temporary tables.

        Args:
            temp_tables: List of table references to drop (same type as operation returns)
        """
        for temp_table in temp_tables:
            self.operation.drop_table(caslib=temp_table.caslib, table=temp_table.name)  # type: ignore
