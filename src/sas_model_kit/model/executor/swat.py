"""SWAT-specific executors.

Executors in this module adapt domain parameters to SWAT actions using
mappers, execute via OperationProtocol, and return pure payloads.
"""

from __future__ import annotations

from typing import Any, cast

from swat.cas import CASResults
from swat.dataframe import SASDataFrame
from typing_extensions import override

from sas_model_kit.model.executor.base import ModelExecutor
from sas_model_kit.model.mapper.base import ParameterMapper
from sas_model_kit.model.mapper.swat import (
    AstoreParameterToSwatDictMapper,
    DataStepParameterToSwatDictMapper,
    ExplainParameterToSwatDictMapper,
)
from sas_model_kit.model.payloads import AstorePayload, DataStepPayload, ExplainPayload
from sas_model_kit.model.types import ShapleyValues
from sas_model_kit.operation import OperationProtocol
from sas_model_kit.parameter import AstoreParameter, DataStepParameter, ExplainParameter


def _extract_timing_ms(result: CASResults) -> float:
    """Extract total execution time in milliseconds from Timing SASDataFrame.

    The astore.score action returns Timing with rows:
    - Loading the Store
    - Creating the State
    - Scoring
    - Total

    Returns:
        Total execution time in milliseconds, or 0.0 if not found.
    """
    if not hasattr(result, "get"):
        return 0.0

    timing: SASDataFrame | None = cast(SASDataFrame | None, result.get("Timing", None))

    if timing is None or timing.empty:
        return 0.0

    try:
        return float(timing[timing["Task"] == "Total"]["Seconds"].values[0]) * 1000.0
    except (IndexError, KeyError, ValueError):
        return 0.0


def _extract_rows_from_output_tables(result: CASResults) -> int:
    """Extract row count from OutputCasTables SASDataFrame.

    The astore.score action returns OutputCasTables with row counts.
    This is more reliable than ScoreInfo.

    Returns:
        Row count from first table, or -1 if not found.
    """
    if hasattr(result, "get"):
        output_tables: SASDataFrame | None = cast(
            SASDataFrame | None, result.get("OutputCasTables", None)
        )
        if output_tables is not None and not output_tables.empty:
            records = output_tables.to_dict(orient="records")
            if records and "Rows" in records[0]:
                return int(records[0]["Rows"])
    return -1


def _extract_rows_scored(result: CASResults) -> int:
    """Best-effort extraction of scored row count from SWAT results.

    Tries multiple sources in order of preference:
    1. OutputCasTables (most reliable)
    2. ScoreInfo (fallback)

    Returns:
        Row count, or -1 if unable to determine.
    """
    # Try OutputCasTables first (most reliable)
    rows = _extract_rows_from_output_tables(result)
    if rows > -1:
        return rows

    # Fallback to ScoreInfo
    score_info = None
    if hasattr(result, "get"):
        score_info = result.get("ScoreInfo") or result.get("scoreinfo")
    if isinstance(score_info, list) and score_info:
        row = score_info[0]
        for key in ("NObs", "NObsUsed", "N", "NObsRead"):
            if isinstance(row, dict) and key in row:
                try:
                    return int(row[key])
                except (TypeError, ValueError):
                    continue
    return -1


def _extract_shapley_values(result: CASResults) -> list[ShapleyValues]:
    if hasattr(result, "get"):
        shapley: SASDataFrame | None = cast(
            SASDataFrame | None, result.get("ShapleyValues", None)
        )

        if shapley is not None and not shapley.empty:
            return shapley.to_dict(orient="records")  # type: ignore[return-value]
    return []


def _extract_status(result: Any) -> tuple[bool, str]:
    # TODO: 尚未被證實
    if hasattr(result, "get"):
        status = result.get("status")
        message = result.get("message") or result.get("reason") or "OK"
        if isinstance(status, bool):
            return status, str(message)
    return True, "OK"


class SwatAstoreExecutor(ModelExecutor[AstoreParameter, AstorePayload]):
    """Execute astore.score via SWAT and return AstorePayload."""

    def __init__(
        self,
        mapper: ParameterMapper[AstoreParameter] | None = None,
    ) -> None:
        self._mapper = mapper or AstoreParameterToSwatDictMapper()

    @override
    def execute(
        self,
        operation: OperationProtocol,
        parameter: AstoreParameter,
        **context: Any,
    ) -> AstorePayload:
        parameter.validate()
        action_dict = self._mapper.map(parameter, **context)
        result = operation.call_action("astore.score", **action_dict)

        casout = action_dict.get("casout", {})
        output_caslib = casout.get("caslib") or ""
        output_table = casout.get("name") or ""
        rows_scored = _extract_rows_scored(result)
        timing_ms = _extract_timing_ms(result)

        # Store timing in context for Model layer to use
        context["execution_time_ms"] = timing_ms

        return AstorePayload(
            output_caslib=output_caslib,
            output_table=output_table,
            rows_scored=rows_scored,
            cas_table=None,
        )


class SwatExplainExecutor(ModelExecutor[ExplainParameter, ExplainPayload]):
    """Execute explainModel.shapleyExplainer via SWAT and return ExplainPayload."""

    def __init__(
        self,
        mapper: ParameterMapper[ExplainParameter] | None = None,
    ) -> None:
        self._mapper = mapper or ExplainParameterToSwatDictMapper()

    @override
    def execute(
        self,
        operation: OperationProtocol,
        parameter: ExplainParameter,
        **context: Any,
    ) -> ExplainPayload:
        parameter.validate()
        action_dict = self._mapper.map(parameter, **context)
        result = operation.call_action("explainModel.shapleyExplainer", **action_dict)

        shapley_values: list[ShapleyValues] = _extract_shapley_values(result)

        query_dict = (
            action_dict.get("query", {}) if isinstance(action_dict, dict) else {}
        )
        output_caslib = query_dict.get("caslib")
        output_table = query_dict.get("name")

        return ExplainPayload(
            shapley_values=shapley_values,
            output_caslib=output_caslib,
            output_table=output_table,
        )


class SwatDataStepExecutor(ModelExecutor[DataStepParameter, DataStepPayload]):
    """Execute datastep.runCode via SWAT and return DataStepPayload."""

    def __init__(
        self,
        mapper: ParameterMapper[DataStepParameter] | None = None,
    ) -> None:
        self._mapper = mapper or DataStepParameterToSwatDictMapper()

    @override
    def execute(
        self,
        operation: OperationProtocol,
        parameter: DataStepParameter,
        **context: Any,
    ) -> DataStepPayload:
        parameter.validate()
        action_dict = self._mapper.map(parameter, **context)
        result = operation.call_action("datastep.runCode", **action_dict)

        success, message = _extract_status(result)
        return DataStepPayload(
            success=success,
            message=message,
            output_caslib=parameter.output_caslib,
            output_table=parameter.output_table,
        )
