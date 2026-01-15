"""SWAT WriteAble + DeleteAble implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from typing_extensions import override

from sas_model_kit.error import OperationError, OperationErrorCode
from sas_model_kit.helpers.protocols import DeleteAble, WriteAble
from sas_model_kit.result import Err, Ok, Result

if TYPE_CHECKING:
    from sas_model_kit.operation import OperationProtocol


class SWATTableLifecycle(WriteAble, DeleteAble):
    """SWAT adapter for table creation and deletion."""

    def __init__(self, operation: OperationProtocol) -> None:
        self.operation = operation

    @override
    def create_table(
        self,
        name: str,
        caslib: str,
        source: Any,
        replace: bool = False,
    ) -> Result[Any, OperationError]:
        """Create or replace a table."""
        try:
            upload_result = self.operation.upload_data(
                data=source,
                caslib=caslib,
                table=name,
                replace=replace,
            )

            if upload_result.is_err:
                return Err(
                    OperationError(
                        code=OperationErrorCode.WRITE_FAILED,
                        message=f"Failed to upload data for table '{name}': {upload_result.error}",
                        cause=upload_result.error,
                    )
                )

            connection = self.operation._session
            new_table = connection.CASTable(name=name, caslib=caslib)
            return Ok(new_table)

        except Exception as e:
            return Err(
                OperationError(
                    code=OperationErrorCode.WRITE_FAILED,
                    message=f"Failed to create table '{name}': {e}",
                    cause=e,
                )
            )

    @override
    def drop_table(self, caslib: str, table: str) -> Result[None, OperationError]:
        """Delete a table from CAS."""
        return self.operation.call_action(
            "table.dropTable",
            caslib=caslib,
            name=table,
        ).map(lambda _: None)


__all__ = ["SWATTableLifecycle"]
