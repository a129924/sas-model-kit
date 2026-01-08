"""BatchExplainProcessor implementation.

Processes multiple IDs by calling explainModel.shapleyExplainer directly
and persists aggregated results as CAS tables.

Design:
    - Direct call_action (no ExplainModel dependency)
    - Generator-based: yields CASTable per ID
    - No intermediate list[dict] conversion (SASDataFrame → transform → upload)
    - Memory-efficient streaming
"""

from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from datetime import datetime
from typing import Any, cast

from pandas import DataFrame
from swat import CASTable, SASDataFrame
from typing_extensions import override

from sas_model_kit.operation import OperationProtocol
from sas_model_kit.parameter import ExplainParameter
from sas_model_kit.processor.base import BaseBatchProcessor, ProcessorResult
from sas_model_kit.processor.executor_batch import BatchOperationExecutor
from sas_model_kit.transformer.shapley_values import ShapleyValuesTransformer


@dataclass(frozen=True)
class BatchExplainProcessor(BaseBatchProcessor["Any"]):
    """Batch processor for Explain executions (CSRP).

    Direct call_action approach:
        - No ExplainModel dependency
        - call_action → SASDataFrame → transform → upload_frame → CASTable
        - Generator yields CASTable
        - concat receives list[CASTable]
    """

    parameter: ExplainParameter
    transformer: ShapleyValuesTransformer
    batch_executor: BatchOperationExecutor

    def __init__(
        self,
        parameter: ExplainParameter,
        operation: OperationProtocol[DataFrame | SASDataFrame],
        *,
        id_column: str = "id",
    ) -> None:
        object.__setattr__(self, "parameter", parameter)
        object.__setattr__(self, "operation", operation)
        object.__setattr__(
            self, "transformer", ShapleyValuesTransformer(id_column=id_column)
        )
        object.__setattr__(self, "batch_executor", BatchOperationExecutor(operation))

    @override
    def process_batch(
        self,
        ids: list[str | int],
        *,
        id_column: str,
        batch_caslib: str,
        output_table: str,
        cleanup_temp_tables: bool = True,
        **context: Any,
    ) -> ProcessorResult[Any]:
        """Process a batch of IDs using direct call_action.

        Flow:
            1. Generator: For each ID, call_action → SASDataFrame
            2. Transform to wide + ID, upload_frame → CASTable
            3. Yield CASTable
            4. Concatenate all CASTable into final output
            5. Cleanup temp tables

        Returns:
            Scheme A semantics:
            - All success: Ok(final_ref)
            - Partial success: Err with partial_output=final_ref
            - All failure: Err with partial_output=None
        """
        cas_tables: list[CASTable] = []
        errors: list[dict[str, Any]] = []

        try:
            batch_prefix = self._generate_batch_id()

            # Generator: yields CASTable per ID
            for item in self._execute_and_upload_generator(
                ids, id_column, batch_prefix, batch_caslib, **context
            ):
                if item["status"] == "success":
                    cas_tables.append(item["cas_table"])
                else:
                    errors.append({"id": item["id"], "message": item["error"]})

            # Concatenate if any CASTable created
            if cas_tables:
                # SWAT concat accepts list[CASTable]
                from swat.cas.table import concat

                concat(
                    cas_tables,
                    casout={
                        "name": output_table,
                        "caslib": batch_caslib,
                        "replace": True,
                    },
                )

            # Cleanup temp tables
            if cleanup_temp_tables and cas_tables:
                temp_tables = [
                    (batch_caslib, str(tbl.params["name"])) for tbl in cas_tables
                ]
                self.batch_executor.cleanup_tables(temp_tables)

            # Scheme A: Return final_ref or partial_output
            final_ref = {"caslib": batch_caslib, "name": output_table}

            if errors:
                return self._err(
                    "BatchExplainProcessor completed with some errors",
                    errors=errors,
                    partial_output=final_ref if cas_tables else None,
                )
            return self._ok(final_ref)

        except Exception as exc:  # pragma: no cover - defensive
            return self._err("BatchExplainProcessor failed", cause=exc)

    def _execute_and_upload_generator(
        self,
        ids: list[str | int],
        id_column: str,
        batch_prefix: str,
        batch_caslib: str,
        **context: Any,
    ) -> Generator[dict[str, Any], None, None]:
        """Generator: call_action → SASDataFrame → transform → upload_frame → CASTable.

        Yields:
            dict with keys: status ("success"|"error"), id, cas_table (if success), error (if error)
        """
        for id_ in ids:
            try:
                # Build where clause
                if isinstance(id_, str):
                    where_value = f"'{id_}'"
                else:
                    where_value = f"{id_}"
                where_clause = f"{id_column}={where_value}"

                # Direct call_action to explainModel.shapleyExplainer
                result = self.operation.call_action(
                    "explainModel.shapleyExplainer",
                    table=self.parameter.train_table,
                    caslib=self.parameter.train_caslib,
                    modelTable=self.parameter.model_table,
                    modelTableType=str(self.parameter.model_table_type),
                    predictedTarget=self.parameter.predicted_target,
                    inputs=self.parameter.features,
                    nominals=[],  # Could be parameterized if needed
                    where=where_clause,
                )

                # Extract SASDataFrame from result['ShapleyValues']
                if not result or "ShapleyValues" not in result:
                    yield {
                        "status": "error",
                        "id": id_,
                        "error": "No ShapleyValues in result",
                    }
                    continue

                shapley_df = cast(
                    SASDataFrame, result["ShapleyValues"]
                )  # This is SASDataFrame

                # Transform: wide + ID (still SASDataFrame)
                wide_df = self.transformer.transform(shapley_df, id_value=id_)

                # Upload DataFrame and create CASTable reference
                table_name = f"{batch_prefix}_{id_column}_{id_}"
                self.operation.upload_data(
                    wide_df, caslib=batch_caslib, table=table_name
                )

                # Create CASTable reference (need connection from operation)
                # For SWAT: operation has _session
                if hasattr(self.operation, "_session"):
                    session = self.operation._session  # type: ignore[attr-defined]
                    cas_table = session.CASTable(name=table_name, caslib=batch_caslib)
                    yield {"status": "success", "id": id_, "cas_table": cas_table}
                else:
                    # Fallback: yield table name for concat
                    yield {
                        "status": "error",
                        "id": id_,
                        "error": "Cannot create CASTable reference",
                    }

            except Exception as e:
                yield {"status": "error", "id": id_, "error": f"Execution failed: {e}"}

    @staticmethod
    def _generate_batch_id() -> str:
        return f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
