"""BatchExplainProcessor implementation.

Processes multiple IDs by calling explainModel.shapleyExplainer directly
and persists aggregated results as CAS tables.

Design (CSRP):
    - Direct call_action (no ExplainModel dependency)
    - Concrete class (not dataclass) inheriting BaseBatchProcessor
    - Generator-based: yields ExecutionSuccess or ExecutionError per ID
    - SASDataFrame → transform → upload → CASTable pipeline
    - Memory-efficient streaming (single-pass)
    - SWAT Bounded Context integration
    - Final dependencies: parameter, transformer, batch_executor, mapper
"""

from __future__ import annotations

from collections.abc import Generator
from datetime import datetime
from typing import Any, Final, cast

from pandas import DataFrame
from swat import CASTable, SASDataFrame
from typing_extensions import override

from sas_model_kit.operation import OperationProtocol
from sas_model_kit.parameter import ExplainParameter
from sas_model_kit.processor.base import (
    BaseBatchProcessor,
    ExecutionError,
    ExecutionItem,
    ExecutionSuccess,
    ProcessorResult,
)
from sas_model_kit.processor.executor_batch import BatchOperationExecutor
from sas_model_kit.processor.swat.mappers import SwatExplainParameterMapper
from sas_model_kit.transformer.shapley_values import ShapleyValuesTransformer


class BatchExplainProcessor(BaseBatchProcessor[dict[str, str]]):
    """Batch processor for Explain executions (CSRP).

    Design:
        - Concrete class (not dataclass) inheriting BaseBatchProcessor
        - Final dependencies: parameter, transformer, batch_executor, mapper
        - @override decorators on all abstract method implementations
        - Immutable: cannot change attributes after __init__

    Direct call_action approach:
        - No ExplainModel dependency
        - call_action → SASDataFrame → transform → upload_frame → CASTable
        - Generator yields ExecutionSuccess or ExecutionError
        - concat receives list[CASTable]
        - Streaming Append: single-pass efficiency (faster than list comprehension)

    Attributes (Final):
        parameter: ExplainParameter with model and feature configuration
        transformer: Converts Shapley SASDataFrame to wide format + ID
        batch_executor: Handles upload/concat/cleanup operations
        mapper: Maps ExplainParameter to SWAT action dictionary
    """

    def __init__(
        self,
        parameter: ExplainParameter,
        operation: OperationProtocol[DataFrame | SASDataFrame, CASTable],
        *,
        id_column: str = "id",
    ) -> None:
        """Initialize BatchExplainProcessor with Final dependencies.

        Args:
            parameter: ExplainParameter with model and feature configuration
            operation: OperationProtocol for call_action and upload_data
            id_column: Column name for ID in results (default: "id")
        """
        object.__setattr__(self, "_parameter", parameter)
        object.__setattr__(self, "_operation", operation)
        object.__setattr__(
            self, "_transformer", ShapleyValuesTransformer(id_column=id_column)
        )
        object.__setattr__(self, "_batch_executor", BatchOperationExecutor(operation))
        object.__setattr__(self, "_mapper", SwatExplainParameterMapper())

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent attribute modification after initialization (immutable)."""
        raise AttributeError(
            f"Cannot modify {self.__class__.__name__}.{name} - instance is immutable"
        )

    @property
    def parameter(self) -> ExplainParameter:
        """Access parameter (read-only)."""
        return object.__getattribute__(self, "_parameter")

    @property
    def operation(self) -> OperationProtocol[DataFrame | SASDataFrame, CASTable]:
        """Access operation (read-only)."""
        return object.__getattribute__(self, "_operation")

    @property
    def transformer(self) -> ShapleyValuesTransformer:
        """Access transformer (read-only)."""
        return object.__getattribute__(self, "_transformer")

    @property
    def batch_executor(self) -> BatchOperationExecutor:
        """Access batch executor (read-only)."""
        return object.__getattribute__(self, "_batch_executor")

    @property
    def mapper(self) -> SwatExplainParameterMapper:
        """Access mapper (read-only)."""
        return object.__getattribute__(self, "_mapper")

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
    ) -> ProcessorResult[dict[str, str]]:
        """Process a batch of IDs using direct call_action.

        Flow:
            1. Generator: For each ID, call_action → SASDataFrame
            2. Transform to wide + ID, upload_frame → CASTable (via upload_data return)
            3. Yield ExecutionSuccess with CASTable
            4. Streaming Append: Collect cas_tables and errors (single-pass, O(n) time)
            5. Concatenate all CASTable into final output
            6. Cleanup temp tables

        Args:
            ids: List of IDs to process
            id_column: Column name for ID filtering
            batch_caslib: CAS library for temporary/output tables
            output_table: Final output table name
            cleanup_temp_tables: Whether to cleanup intermediate tables (default: True)
            **context: Additional execution context

        Returns:
            Scheme A semantics:
            - All success: Ok(final_ref)
            - Partial success: Err with partial_output=final_ref
            - All failure: Err with partial_output=None

        Example:
            >>> processor = BatchExplainProcessor(param, operation)
            >>> result = processor.process_batch(
            ...     ids=["id1", "id2", "id3"],
            ...     id_column="id",
            ...     batch_caslib="public",
            ...     output_table="explain_results",
            ... )
            >>> if result.is_ok:
            ...     final_ref = result.unwrap()
            ...     print(f"Results in {final_ref['name']}")
        """
        cas_tables: list[CASTable] = []
        errors: list[dict[str, Any]] = []

        try:
            batch_prefix = self._generate_batch_id()

            # Streaming Append (single-pass, O(n) - fastest approach)
            for result in self._execute_and_upload_generator(
                ids, id_column, batch_prefix, batch_caslib, **context
            ):
                if isinstance(result, ExecutionSuccess):
                    cas_tables.append(result.cas_table)
                elif isinstance(result, ExecutionError):
                    errors.append({"id": result.id, "message": result.message})

            # Concatenate if any CASTable created
            if cas_tables:
                # SWAT concat accepts list[CASTable]
                # Reference: #sym:concat in swat/cas/table.py
                from swat.cas.table import concat

                final_castable = concat(
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
    ) -> Generator[ExecutionItem, None, None]:
        """Generator: call_action → SASDataFrame → transform → upload_frame → CASTable.

        Yields:
            ExecutionSuccess(id, cas_table) or ExecutionError(id, message) per iteration

        Memory Efficiency:
            - No list accumulation (generator)
            - SASDataFrame handled natively (not converted to list[dict])
            - CASTable reference held briefly for concat
            - Single-pass iteration

        Example:
            >>> for result in self._execute_and_upload_generator(
            ...     ids=["id1", "id2"],
            ...     id_column="id",
            ...     batch_prefix="batch_20260108_120000",
            ...     batch_caslib="public",
            ... ):
            ...     if isinstance(result, ExecutionSuccess):
            ...         print(f"ID {result.id} succeeded")
            ...     else:
            ...         print(f"ID {result.id} failed: {result.message}")
        """
        for id_ in ids:
            try:
                # Build where clause
                if isinstance(id_, str):
                    where_value = f"'{id_}'"
                else:
                    where_value = f"{id_}"
                where_clause = f"{id_column}={where_value}"

                # Use mapper to build action dictionary (avoiding hardcoding)
                action_dict = self.mapper.build_action_dict(
                    self.parameter,
                    where=where_clause,
                    **context,
                )

                # Direct call_action to explainModel.shapleyExplainer
                result = self.operation.call_action(
                    "explainModel.shapleyExplainer",
                    **action_dict,
                )

                # Extract SASDataFrame from result['ShapleyValues']
                if not result or "ShapleyValues" not in result:
                    yield ExecutionError(
                        id=id_,
                        message="No ShapleyValues in result",
                    )
                    continue

                shapley_df = cast(
                    SASDataFrame, result["ShapleyValues"]
                )  # This is SASDataFrame

                # Transform: wide + ID (still SASDataFrame)
                wide_df = self.transformer.transform(shapley_df, id_value=id_)

                # Upload DataFrame and get CASTable reference (new feature!)
                # upload_data now returns CASTable (was None before)
                table_name = f"{batch_prefix}_{id_column}_{id_}"
                cas_table = self.operation.upload_data(
                    wide_df, caslib=batch_caslib, table=table_name
                )

                # Type-safe yield with ExecutionSuccess dataclass
                yield ExecutionSuccess(id=id_, cas_table=cas_table)

            except Exception as e:
                # Type-safe yield with ExecutionError dataclass
                yield ExecutionError(id=id_, message=f"Execution failed: {e}")

    @staticmethod
    def _generate_batch_id() -> str:
        """Generate unique batch ID for temporary tables."""
        return f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
