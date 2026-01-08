"""Tests for BatchExplainProcessor.

Tests direct call_action approach without ExplainModel dependency.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

from swat import CASTable
from swat.dataframe import SASDataFrame

from sas_model_kit.model.types import ModelTableType
from sas_model_kit.operation import OperationProtocol
from sas_model_kit.parameter import ExplainParameter
from sas_model_kit.processor import BatchExplainProcessor


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


class TestBatchExplainProcessor:
    def test_successful_batch_with_concat_and_cleanup(self) -> None:
        """Test successful batch processing with concat and cleanup."""
        operation = Mock(spec=OperationProtocol)
        operation._session = Mock()  # SWAT session for CASTable creation

        # Mock call_action to return shapley result
        shapley_df = SASDataFrame({"Variable": ["age"], "ShapleyValue": [0.1]})
        operation.call_action.return_value = {"ShapleyValues": shapley_df}

        # Mock CASTable creation
        mock_table = Mock(spec=CASTable)
        mock_table.params = {"name": "batch_123_customer_id_A"}
        operation._session.CASTable.return_value = mock_table

        processor = BatchExplainProcessor(
            parameter=_make_param(), operation=operation, id_column="customer_id"
        )

        # Mock concat to avoid real SWAT call
        with patch("swat.cas.table.concat") as mock_concat:
            result = processor.process_batch(
                ids=["A", "B"],
                id_column="customer_id",
                batch_caslib="public",
                output_table="explain_out",
                cleanup_temp_tables=True,
            )

            assert result.is_ok
            final = result.unwrap()
            assert final == {"caslib": "public", "name": "explain_out"}

            # Verify explainModel.shapleyExplainer was called for each ID (2 calls)
            # Plus upload_data (2 calls via batch_executor) and cleanup dropTable (2 calls)
            explain_calls = [
                c
                for c in operation.call_action.call_args_list
                if c[0][0] == "explainModel.shapleyExplainer"
            ]
            assert len(explain_calls) == 2
            # Verify concat was called
            mock_concat.assert_called_once()

    def test_partial_failures_with_partial_output(self) -> None:
        """Test partial failure returns Err with partial_output."""
        operation = Mock(spec=OperationProtocol)
        operation._session = Mock()

        # First ID succeeds, second fails
        shapley_df = SASDataFrame({"Variable": ["age"], "ShapleyValue": [0.1]})
        operation.call_action.side_effect = [
            {"ShapleyValues": shapley_df},
            Exception("ID not found"),
        ]

        mock_table = Mock(spec=CASTable)
        mock_table.params = {"name": "batch_123_customer_id_1"}
        operation._session.CASTable.return_value = mock_table

        processor = BatchExplainProcessor(parameter=_make_param(), operation=operation)

        with patch("swat.cas.table.concat"):
            result = processor.process_batch(
                ids=[1, 2],
                id_column="customer_id",
                batch_caslib="pub",
                output_table="out",
                cleanup_temp_tables=False,
            )

            assert result.is_err
            err = result.error
            assert "some errors" in err.message
            assert err.partial_output is not None
            assert err.partial_output["name"] == "out"

    def test_empty_ids_returns_ok(self) -> None:
        """Empty ID list should succeed without any operations."""
        operation = Mock(spec=OperationProtocol)
        processor = BatchExplainProcessor(parameter=_make_param(), operation=operation)

        result = processor.process_batch(
            ids=[],
            id_column="customer_id",
            batch_caslib="public",
            output_table="out",
        )

        assert result.is_ok
        operation.call_action.assert_not_called()

    def test_all_failures_no_partial_output(self) -> None:
        """All failures should return Err with partial_output=None."""
        operation = Mock(spec=OperationProtocol)
        operation.call_action.side_effect = [
            Exception("Error 1"),
            Exception("Error 2"),
        ]

        processor = BatchExplainProcessor(parameter=_make_param(), operation=operation)

        result = processor.process_batch(
            ids=["X", "Y"],
            id_column="customer_id",
            batch_caslib="public",
            output_table="out",
        )

        assert result.is_err
        err = result.error
        assert err.partial_output is None
        assert len(err.errors) == 2  # type: ignore[arg-type]

    def test_string_vs_numeric_id_formatting(self) -> None:
        """Test WHERE clause formatting for string vs numeric IDs."""
        operation = Mock(spec=OperationProtocol)
        operation._session = Mock()

        shapley_df = SASDataFrame({"Variable": ["age"], "ShapleyValue": [0.1]})
        operation.call_action.return_value = {"ShapleyValues": shapley_df}

        mock_table = Mock()
        mock_table.params = {"name": "batch_123_id_A"}
        operation._session.CASTable.return_value = mock_table

        processor = BatchExplainProcessor(parameter=_make_param(), operation=operation)

        processor.process_batch(
            ids=["str_id", 123],
            id_column="id",
            batch_caslib="pub",
            output_table="out",
        )

        # Check WHERE clauses
        calls = operation.call_action.call_args_list
        assert calls[0][1]["where"] == "id='str_id'"
        assert calls[1][1]["where"] == "id=123"
