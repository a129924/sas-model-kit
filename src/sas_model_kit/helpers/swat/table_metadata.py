"""SWAT ReadAble + ValidateAble implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import override

from sas_model_kit.error import OperationError, OperationErrorCode, TableNotFoundError
from sas_model_kit.helpers.protocols import ReadAble, ValidateAble
from sas_model_kit.helpers.swat.types import SwatTableT
from sas_model_kit.result import Err, Ok, Result

if TYPE_CHECKING:
    from sas_model_kit.operation import OperationProtocol


class SWATTableMetadata(ReadAble[SwatTableT], ValidateAble[SwatTableT]):
    """SWAT adapter for table metadata and existence checks."""

    def __init__(self, operation: OperationProtocol) -> None:
        self.operation = operation

    @override
    def get_columns(self, table: SwatTableT) -> Result[list[str], OperationError]:
        """Get all column names from the table."""
        try:
            return Ok(list(table.columns))
        except Exception as e:
            return Err(
                OperationError(
                    code=OperationErrorCode.READ_FAILED,
                    message=f"Failed to get columns: {e}",
                    cause=e,
                )
            )

    @override
    def get_table_location(
        self, table: SwatTableT
    ) -> Result[tuple[str, str], OperationError]:
        """Get table location as (caslib, table_name)."""
        try:
            caslib = table.params.get("caslib", "public")
            name = table.params["name"]
            return Ok((caslib, name))
        except Exception as e:
            return Err(
                OperationError(
                    code=OperationErrorCode.READ_FAILED,
                    message=f"Failed to get table location: {e}",
                    cause=e,
                )
            )

    @override
    def ensure_exists(
        self, library_table: SwatTableT
    ) -> Result[SwatTableT, TableNotFoundError]:
        """Validate CAS table exists using native exists() method."""
        try:
            if library_table.exists():
                return Ok(library_table)

            table_name = library_table.params.get("name", "unknown")
            caslib = library_table.params.get("caslib", "ACTIVE")
            return Err(
                TableNotFoundError(
                    message=f"Table '{table_name}' not found in caslib '{caslib}'"
                )
            )
        except Exception as e:
            return Err(
                TableNotFoundError(
                    message=f"Failed to check table existence: {e}",
                    cause=e,
                )
            )

    @override
    def ensure_columns_exist(
        self, table: SwatTableT, required_columns: list[str]
    ) -> Result[SwatTableT, OperationError]:
        """Validate that required columns exist on table.

        Returns Ok(table) if all required columns are present; otherwise Err(OperationError).
        """
        try:
            cols = set(map(str, table.columns))  # type: ignore
            missing = [c for c in required_columns if str(c) not in cols]
            if missing:
                return Err(
                    OperationError(
                        code=OperationErrorCode.READ_FAILED,
                        message=f"Missing required columns: {missing}",
                    )
                )
            return Ok(table)
        except Exception as e:
            return Err(
                OperationError(
                    code=OperationErrorCode.READ_FAILED,
                    message=f"Failed to validate columns {required_columns}: {e}",
                    cause=e,
                )
            )


__all__ = ["SWATTableMetadata"]
