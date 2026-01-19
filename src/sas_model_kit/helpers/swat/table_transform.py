"""SWAT SortAble + ConcatAble implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from swat.exceptions import SWATError
from typing_extensions import override

from sas_model_kit.error import OperationError, OperationErrorCode
from sas_model_kit.helpers.protocols import ConcatAble, SortAble
from sas_model_kit.helpers.swat.types import SwatTableT
from sas_model_kit.result import Err, Ok, Result

if TYPE_CHECKING:
    from sas_model_kit.operation import OperationProtocol

try:
    from swat.cas.table import CASTable
except ImportError:
    raise ImportError(
        "SWAT is required for SWATTableTransform. Please install SWAT to use this feature."
    ) from ImportError


class SWATTableTransform(SortAble[CASTable], ConcatAble[CASTable]):
    """SWAT adapter for table sorting and concatenation."""

    def __init__(self, operation: OperationProtocol) -> None:
        self.operation = operation

    @override
    def sort_values(
        self,
        table: CASTable,
        by: list[str],
        ascending: bool | list[bool] = True,
    ) -> Result[CASTable, OperationError]:
        """
        Sort table by specified columns.

        """
        try:
            sorted_table = cast(CASTable, table.sort_values(by=by, ascending=ascending))  # type: ignore
            return Ok(sorted_table)
        except Exception as e:
            return Err(
                OperationError(
                    code=OperationErrorCode.SORT_FAILED,
                    message=f"Failed to sort table by {by}: {e}",
                    cause=e,
                )
            )

    @override
    def concat_tables(
        self,
        inputs: list[SwatTableT],
        caslib: str,
        output_table: str,
        replace: bool = True,
    ) -> Result[SwatTableT, OperationError]:
        """Concatenate multiple tables into one."""
        from swat.functions import concat

        try:
            concatenated_table = cast(
                SwatTableT,
                concat(inputs, caslib=caslib, name=output_table, replace=replace),
            )

            return Ok(concatenated_table)
        except SWATError as swat_err:
            return Err(
                OperationError(
                    code=OperationErrorCode.WRITE_FAILED,
                    message=f"Failed to concatenate tables into '{output_table}': {swat_err}",
                    cause=swat_err,
                )
            )
        except Exception as e:
            return Err(
                OperationError(
                    code=OperationErrorCode.UNKNOWN,
                    message=f"Unknown error concatenating tables into '{output_table}': {e}",
                    cause=e,
                )
            )


__all__ = ["SWATTableTransform"]
