"""Tests for BatchOperationExecutor."""

from unittest.mock import Mock

from swat.dataframe import SASDataFrame

from sas_model_kit.processor.executor_batch import BatchOperationExecutor


def test_upload_dataframe_calls_operation_upload() -> None:
    op = Mock()
    execu = BatchOperationExecutor(op)
    df = SASDataFrame({"a": [1], "b": [2]})

    execu.upload_dataframe(df, caslib="public", table="t1")

    op.upload_data.assert_called_once_with(df, caslib="public", table="t1")


def test_concat_tables_calls_table_concat() -> None:
    op = Mock()
    execu = BatchOperationExecutor(op)

    inputs = [
        {"name": "tmp1", "caslib": "public"},
        {"name": "tmp2", "caslib": "public"},
    ]
    execu.concat_tables(inputs, caslib="public", output_table="final", replace=True)

    op.call_action.assert_called_once()
    action, kwargs = op.call_action.call_args[0][0], op.call_action.call_args[1]
    assert action == "table.concat"
    assert kwargs["casout"]["name"] == "final"
    assert kwargs["casout"]["caslib"] == "public"
    assert kwargs["casout"]["replace"] is True
    assert kwargs["inputs"] == inputs


def test_cleanup_tables_calls_dropTable() -> None:
    op = Mock()
    execu = BatchOperationExecutor(op)

    temp = [("public", "tmp1"), ("public", "tmp2")]
    execu.cleanup_tables(temp)

    assert op.call_action.call_count == 2
    for call in op.call_action.call_args_list:
        assert call[0][0] == "table.dropTable"
        assert call[1]["quiet"] is True
