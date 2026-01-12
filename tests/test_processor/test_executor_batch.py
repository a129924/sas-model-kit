"""Tests for BatchOperationExecutor."""

from unittest.mock import Mock

from sas_model_kit.processor.executor_batch import BatchOperationExecutor


def test_upload_dataframe_calls_operation_upload() -> None:
    op = Mock()
    execu = BatchOperationExecutor(op)

    # Create a mock DataSource
    datasource = Mock()
    execu.upload_dataframe(datasource)

    datasource.prepare.assert_called_once_with(op)


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

    # Create mock tables with caslib and name attributes
    mock_table1 = Mock()
    mock_table1.caslib = "public"
    mock_table1.name = "tmp1"
    mock_table2 = Mock()
    mock_table2.caslib = "public"
    mock_table2.name = "tmp2"

    temp = [mock_table1, mock_table2]
    execu.cleanup_tables(temp)

    assert op.drop_table.call_count == 2
    # Verify both tables were dropped
    op.drop_table.assert_any_call(caslib="public", table="tmp1")
    op.drop_table.assert_any_call(caslib="public", table="tmp2")
