"""Tests for BaseError and ErrorProtocol."""

import pytest

from sas_model_kit.error import BaseError, ErrorProtocol, ErrorSeverity


def test_base_error_to_dict() -> None:
    err = BaseError(code="E001", message="something bad")
    data = err.to_dict()
    assert data["code"] == "E001"
    assert data["message"] == "something bad"
    assert data["severity"] == ErrorSeverity.ERROR.value
    assert data["context"] == {}


def test_base_error_custom_severity_and_context() -> None:
    err = BaseError(
        code="E002",
        message="warn",
        severity=ErrorSeverity.WARNING,
        context={"field": "age"},
    )
    data = err.to_dict()
    assert data["severity"] == "warning"
    assert data["context"] == {"field": "age"}


def test_base_error_is_protocol_compliant() -> None:
    err: ErrorProtocol = BaseError(code="E003", message="proto")
    assert err.code == "E003"
    assert err.message == "proto"
    assert err.severity is ErrorSeverity.ERROR
    assert err.context == {}


def test_print_debug_info_handles_none_cause(
    capsys: pytest.CaptureFixture[str],
) -> None:
    err = BaseError(code="E004", message="no cause")
    err.print_debug_info()
    captured = capsys.readouterr()
    assert captured.err == ""


def test_print_debug_info_includes_cause(capsys: pytest.CaptureFixture[str]) -> None:
    cause = ValueError("boom")
    err = BaseError(code="E005", message="has cause", cause=cause)
    err.print_debug_info()
    captured = capsys.readouterr()
    assert "ValueError" in captured.err
    assert "boom" in captured.err
