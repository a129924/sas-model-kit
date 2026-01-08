"""Batch Operation Executor.

Encapsulates common batch-oriented CAS operations used by processors,
keeping processors focused on orchestration logic.

Responsibilities (CSRP):
    - Upload DataFrame to CAS
    - Concatenate temporary tables into final output
    - Cleanup temporary tables
"""

from __future__ import annotations

from typing import Any

from swat.dataframe import SASDataFrame

from sas_model_kit.operation import OperationProtocol


class BatchOperationExecutor:
    """Executor for common batch operations over OperationProtocol."""

    def __init__(self, operation: OperationProtocol[SASDataFrame]) -> None:
        self.operation = operation

    def upload_dataframe(self, df: SASDataFrame, *, caslib: str, table: str) -> None:
        """Upload a SASDataFrame to CAS."""
        self.operation.upload_data(df, caslib=caslib, table=table)

    def concat_tables(
        self,
        inputs: list[dict[str, str]],
        *,
        caslib: str,
        output_table: str,
        replace: bool = True,
    ) -> Any:
        """Concatenate input tables into a single output table."""
        return self.operation.call_action(
            "table.concat",
            casout={"name": output_table, "caslib": caslib, "replace": replace},
            inputs=inputs,
        )

    def cleanup_tables(self, temp_tables: list[tuple[str, str]]) -> None:
        """Drop temporary tables created during batch processing."""
        for caslib, name in temp_tables:
            self.operation.call_action(
                "table.dropTable", name=name, caslib=caslib, quiet=True
            )
