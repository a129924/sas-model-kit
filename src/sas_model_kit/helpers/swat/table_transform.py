"""SWAT SortAble + ConcatAble implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from typing_extensions import override
from swat.exceptions import SWATError

from sas_model_kit.error import OperationError, OperationErrorCode
from sas_model_kit.error.operation import ConcatTableError
from sas_model_kit.error.transformer import SortError
from sas_model_kit.helpers.protocols import ConcatAble, SortAble
from sas_model_kit.helpers.swat.types import SwatTableT
from sas_model_kit.result import Err, Ok, Result

if TYPE_CHECKING:
    from sas_model_kit.operation import OperationProtocol


class SWATTableTransform(SortAble[SwatTableT], ConcatAble[SwatTableT]):
    """SWAT adapter for table sorting and concatenation."""

    def __init__(self, operation: OperationProtocol) -> None:
        self.operation = operation

    @override
    def sort_values(
        self,
        table: SwatTableT,
        by: list[str],
        ascending: bool | list[bool] = True,
    ) -> Result[SwatTableT, OperationError]:
        """
        Sort table by specified columns.

        """
        try:
            sorted_table = table.sort_values(by=by, ascending=ascending)
            return Ok(sorted_table)
        except Exception as e:
            return OperationError(
                code=OperationErrorCode.SWAT_EXECUTION_ERROR,
                message=f"Failed to sort table by {by}: {e}",
                cause=e,
            )

    @override
    def concat_tables(
        self,
        inputs: list[SwatTableT],
        caslib: str,
        output_table: str,
        replace: bool = True,
    ) -> Result[SwatTableT, ConcatTableError | OperationError]:
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
                ConcatTableError(
                    message=f"Failed to concatenate tables into '{output_table}': {swat_err}",
                    cause=swat_err,
                )
            )
        except Exception as e:
            return Err(
                OperationError(
                    code=OperationErrorCode.SWAT_EXECUTION_ERROR,
                    message=f"Unknown error concatenating tables into '{output_table}': {e}",
                    cause=e,
                )
            )


__all__ = ["SWATTableTransform"]
