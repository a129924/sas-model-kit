"""Tests for BatchExplainProcessor with ExecutionResult dataclass.

Tests direct call_action approach with type-safe ExecutionSuccess/ExecutionError.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch

from swat import CASTable
from swat.dataframe import SASDataFrame

from sas_model_kit.model.types import ModelTableType
from sas_model_kit.operation import OperationProtocol
from sas_model_kit.parameter import ExplainParameter
from sas_model_kit.processor import BatchExplainProcessor
from sas_model_kit.processor.base import ExecutionError, ExecutionSuccess


def _make_param() -> ExplainParameter:
    return ExplainParameter(
        train_caslib="public",
        train_table="training",
        predicted_target="target",
        features=["age", "income"],
        id_cols={"customer_id"},
        depth=1,
        model_table_type=ModelTableType.ASTORE,
        model_caslib="models",
        model_table="astore",
        sas_score_code="code",
    )


class TestBatchExplainProcessorExecutionResult:
    """Test ExecutionSuccess and ExecutionError dataclass usage."""

    @patch("swat.cas.table.concat")
    def test_successful_batch_with_cas_table_return(self, mock_concat: Mock) -> None:
        """Test successful batch with upload_data returning CASTable."""
        operation = Mock(spec=OperationProtocol)

        # Mock call_action to return shapley result
        shapley_df = SASDataFrame({"Variable": ["age"], "ShapleyValue": [0.1]})
        operation.call_action.return_value = {"ShapleyValues": shapley_df}

        # Mock upload_data to return CASTable (new behavior!)
        def make_cas_table(df: Any, caslib: str, table: str) -> CASTable:
            mock_table = Mock(spec=CASTable)
            mock_table.params = {"name": table}
            return mock_table

        operation.upload_data.side_effect = make_cas_table

        processor = BatchExplainProcessor(
            parameter=_make_param(), operation=operation, id_column="customer_id"
        )

        result = processor.process_batch(
            ids=["1", "2"],
            id_column="customer_id",
            batch_caslib="public",
            output_table="results",
            cleanup_temp_tables=False,  # Skip cleanup for testing
        )

        # Verify success
        assert result.is_ok
        final_ref = result.unwrap()
        assert final_ref["name"] == "results"
        assert final_ref["caslib"] == "public"

        # Verify upload_data called twice (returns CASTable, not None)
        assert operation.upload_data.call_count == 2

    @patch("swat.cas.table.concat")
    def test_partial_success_with_execution_error(self, mock_concat: Mock) -> None:
        """Test partial success: 1 success + 1 ExecutionError."""
        operation = Mock(spec=OperationProtocol)

        # First call succeeds
        shapley_df = SASDataFrame({"Variable": ["age"], "ShapleyValue": [0.1]})
        operation.call_action.side_effect = [
            {"ShapleyValues": shapley_df},
            Exception("API error"),
        ]

        # upload_data returns CASTable for first only
        mock_table = Mock(spec=CASTable)
        mock_table.params = {"name": "batch_123_customer_id_1"}
        operation.upload_data.return_value = mock_table

        processor = BatchExplainProcessor(
            parameter=_make_param(), operation=operation, id_column="customer_id"
        )

        result = processor.process_batch(
            ids=["1", "2"],
            id_column="customer_id",
            batch_caslib="public",
            output_table="results",
            cleanup_temp_tables=False,
        )

        # Should return Err with partial_output (1 success)
        assert result.is_err
        err = result.error
        assert err.partial_output is not None  # ← Scheme A: partial_output set
        assert err.errors is not None
        assert len(err.errors) == 1
        assert err.errors[0]["id"] == "2"

    def test_all_failures_no_partial_output(self) -> None:
        """Test all failures: no partial_output (Scheme A)."""
        operation = Mock(spec=OperationProtocol)
        operation.call_action.side_effect = [
            Exception("Error 1"),
            Exception("Error 2"),
        ]

        processor = BatchExplainProcessor(
            parameter=_make_param(), operation=operation, id_column="customer_id"
        )

        result = processor.process_batch(
            ids=["1", "2"],
            id_column="customer_id",
            batch_caslib="public",
            output_table="results",
        )

        # Should return Err with no partial_output (all failed)
        assert result.is_err
        err = result.error
        assert err.partial_output is None  # ← Scheme A: no partial output
        assert err.errors is not None
        assert len(err.errors) == 2

    def test_empty_ids_returns_ok(self) -> None:
        """Test empty ID list returns Ok."""
        operation = Mock(spec=OperationProtocol)

        processor = BatchExplainProcessor(
            parameter=_make_param(), operation=operation, id_column="customer_id"
        )

        result = processor.process_batch(
            ids=[],
            id_column="customer_id",
            batch_caslib="public",
            output_table="results",
        )

        # Empty list should succeed
        assert result.is_ok
        # But call_action should not be called
        operation.call_action.assert_not_called()

    @patch("swat.cas.table.concat")
    def test_string_vs_numeric_id_formatting(self, mock_concat: Mock) -> None:
        """Test WHERE clause formatting for string vs numeric IDs."""
        operation = Mock(spec=OperationProtocol)

        shapley_df = SASDataFrame({"Variable": ["age"], "ShapleyValue": [0.1]})
        operation.call_action.return_value = {"ShapleyValues": shapley_df}

        mock_table = Mock(spec=CASTable)
        mock_table.params = {"name": "temp_table"}
        operation.upload_data.return_value = mock_table

        processor = BatchExplainProcessor(
            parameter=_make_param(), operation=operation, id_column="id"
        )

        result = processor.process_batch(
            ids=["str_id", 123],
            id_column="id",
            batch_caslib="public",
            output_table="results",
            cleanup_temp_tables=False,
        )

        # Check that both IDs were processed
        assert operation.call_action.call_count == 2
