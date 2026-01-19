"""Ultra-light Facades for common Able compositions (Result monadic chaining).

These facades provide minimal, 3-5 line conveniences to compose validation
and pure transforms, keeping responsibilities separated per Option A.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from typing_extensions import override

from sas_model_kit.helpers.protocols import (
    ConcatAble,
    SortAble,
    ValidateAble,
)
from sas_model_kit.helpers.swat.types import SwatTableT
from sas_model_kit.result import Result

if TYPE_CHECKING:
    from sas_model_kit.operation import OperationProtocol

try:
    from swat.cas.table import CASTable
except ImportError:
    raise ImportError(
        "SWAT is required for SWATTableTransform. Please install SWAT to use this feature."
    ) from ImportError


class ValidateAndSortFacade:
    """Facade: ensure exists + ensure columns + sort.

    Keeps methods minimal by leveraging Result.and_then for error propagation.
    """

    def __init__(
        self,
        validatable: ValidateAble[CASTable],
        sortable: SortAble[CASTable],
    ) -> None:
        self.validatable = validatable
        self.sortable = sortable

    def sort_with_validation(
        self,
        table: CASTable,
        by: list[str],
        ascending: bool | list[bool] = True,
    ) -> Result[CASTable, Any]:
        return (
            self.validatable.ensure_exists(table)
            .and_then(lambda t: self.validatable.ensure_columns_exist(t, by))
            .and_then(
                lambda t: self.sortable.sort_values(t, by=by, ascending=ascending)
            )
        )


class ValidateAndConcatFacade:
    """Facade: ensure exists + ensure columns + concat.

    Validates each input table for existence; optional schema validation is
    handled by callers prior to concat if needed.
    """

    def __init__(
        self,
        validatable: ValidateAble[SwatTableT],
        concatable: ConcatAble[SwatTableT],
    ) -> None:
        self.validatable = validatable
        self.concatable = concatable

    @override
    def concat_with_validation(
        self,
        inputs: list[SwatTableT],
        caslib: str,
        output_table: str,
        replace: bool = True,
    ) -> Result[SwatTableT, Any]:
        def validate_all(ts: list[SwatTableT]) -> Result[list[SwatTableT], Any]:
            # Chain validations sequentially using fold-like pattern
            from sas_model_kit.result import Ok, Err

            validated: list[SwatTableT] = []
            for t in ts:
                r = self.validatable.ensure_exists(t)
                if r.is_err():
                    # Propagate first error encountered
                    return Err(r.error)
                validated.append(r.value)
            return Ok(validated)

        return validate_all(inputs).and_then(
            lambda vs: self.concatable.concat_tables(
                inputs=vs, caslib=caslib, output_table=output_table, replace=replace
            )
        )


__all__ = ["ValidateAndSortFacade", "ValidateAndConcatFacade"]
