"""SWAT ActionExecutable + ResultParseable implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from typing_extensions import override

from sas_model_kit.error import OperationError, OperationErrorCode
from sas_model_kit.helpers.protocols import ActionExecutable, ModelResultParseable
from sas_model_kit.result import Err, Ok, Result

if TYPE_CHECKING:
    from sas_model_kit.operation import OperationProtocol


class SWATActionProcessor(ActionExecutable, ModelResultParseable):
    """SWAT adapter for action execution and result parsing."""

    def __init__(self, operation: OperationProtocol) -> None:
        self.operation = operation

    @override
    def execute_action(self, action: str, **kwargs: Any) -> Result[Any, OperationError]:
        """Execute a SWAT action."""
        return self.operation.call_action(action, **kwargs)

    @override
    def extract_astore_payload(
        self, result: Any
    ) -> Result[dict[str, Any], OperationError]:
        """Extract astore.score payload from result."""
        try:
            if hasattr(result, "get"):
                output_tables = result.get("OutputCasTables", None)
                if output_tables is not None:
                    payload = {
                        "output_tables": output_tables.to_dict(orient="records"),
                    }
                    return Ok(payload)

            return Ok({})

        except Exception as e:
            return Err(
                OperationError(
                    code=OperationErrorCode.PARSE_FAILED,
                    message=f"Failed to extract astore payload: {e}",
                    cause=e,
                )
            )

    @override
    def extract_shapley_values(
        self,
        result: Any,
    ) -> Result[list[dict[str, Any]], OperationError]:
        """Extract Shapley values from result."""
        try:
            if hasattr(result, "get"):
                shapley = result.get("ShapleyValues", None)
                if shapley is not None:
                    return Ok(shapley.to_dict(orient="records"))

            return Ok([])

        except Exception as e:
            return Err(
                OperationError(
                    code=OperationErrorCode.PARSE_FAILED,
                    message=f"Failed to extract Shapley values: {e}",
                    cause=e,
                )
            )

    @override
    def extract_status(self, result: Any) -> Result[tuple[bool, str], OperationError]:
        """Parse action status from result."""
        try:
            if hasattr(result, "get"):
                status = result.get("status")
                message = result.get("message") or "OK"

                if isinstance(status, bool):
                    return Ok((status, str(message)))

            return Ok((True, "OK"))

        except Exception as e:
            return Err(
                OperationError(
                    code=OperationErrorCode.PARSE_FAILED,
                    message=f"Failed to extract status: {e}",
                    cause=e,
                )
            )


__all__ = ["SWATActionProcessor"]
