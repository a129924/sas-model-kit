"""Tests for Rust-style Result base classes."""

import pytest

from sas_model_kit.result.base import Err, Ok, Result


def test_ok_creation() -> None:
    """Test Ok instance creation."""
    result = Ok(42)
    assert result.is_ok
    assert not result.is_err
    assert result.unwrap() == 42


def test_ok_with_none_value() -> None:
    """Test Ok can hold None value."""
    result = Ok(None)
    assert result.is_ok
    assert result.unwrap() is None


def test_ok_with_complex_type() -> None:
    """Test Ok with complex data types."""
    data = {"key": "value", "count": 42}
    result = Ok(data)
    assert result.is_ok
    assert result.unwrap() == data


def test_err_creation() -> None:
    """Test Err instance creation."""
    error = ValueError("test error")
    result = Err(error)
    assert result.is_err
    assert not result.is_ok
    assert result.error == error


def test_err_with_string() -> None:
    """Test Err with string error."""
    result = Err("error message")
    assert result.is_err
    assert result.error == "error message"


def test_unwrap_ok_returns_value() -> None:
    """Test unwrap on Ok returns the value."""
    result = Ok(42)
    assert result.unwrap() == 42


def test_unwrap_err_raises_exception() -> None:
    """Test unwrap on Err raises the contained exception."""
    error = ValueError("test error")
    result = Err(error)

    with pytest.raises(ValueError, match="test error"):
        result.unwrap()


def test_unwrap_err_with_non_exception_raises_runtime_error() -> None:
    """Test unwrap on Err with non-Exception raises RuntimeError."""
    result = Err("string error")

    with pytest.raises(RuntimeError, match="Result is Err: string error"):
        result.unwrap()


def test_unwrap_or_ok_returns_value() -> None:
    """Test unwrap_or on Ok returns the value, not default."""
    result = Ok(42)
    assert result.unwrap_or(0) == 42


def test_unwrap_or_err_returns_default() -> None:
    """Test unwrap_or on Err returns the default value."""
    result: Result[int, str] = Err("error")
    assert result.unwrap_or(0) == 0


def test_unwrap_or_with_none_default() -> None:
    """Test unwrap_or with None as default."""
    result: Result[int, str] = Err("error")
    assert result.unwrap_or(None) is None


def test_unwrap_or_else_ok_returns_value() -> None:
    """Test unwrap_or_else on Ok returns the value."""
    result = Ok(42)
    assert result.unwrap_or_else(lambda e: 0) == 42


def test_unwrap_or_else_err_calls_function() -> None:
    """Test unwrap_or_else on Err calls the provided function."""
    result: Result[int, str] = Err("error")
    assert result.unwrap_or_else(lambda e: len(e)) == 5


def test_unwrap_or_else_with_complex_computation() -> None:
    """Test unwrap_or_else with complex error handling."""
    result: Result[int, ValueError] = Err(ValueError("test"))
    default = result.unwrap_or_else(lambda e: len(str(e)))
    assert default == 4  # len("test")


def test_ok_is_frozen() -> None:
    """Test that Ok instances are immutable."""
    result = Ok(42)
    with pytest.raises(AttributeError):
        result.value = 100  # type: ignore[misc]


def test_err_is_frozen() -> None:
    """Test that Err instances are immutable."""
    result = Err("error")
    with pytest.raises(AttributeError):
        result.error = "new error"  # type: ignore[misc]


def test_type_checking_ok() -> None:
    """Test type narrowing for Ok."""
    result: Result[int, str] = Ok(42)

    if result.is_ok:
        # Type checker should know this is Ok
        value = result.value
        assert value == 42


def test_type_checking_err() -> None:
    """Test type narrowing for Err."""
    result: Result[int, str] = Err("failed")

    if result.is_err:
        # Type checker should know this is Err
        error = result.error
        assert error == "failed"


def test_ok_repr() -> None:
    """Test Ok string representation."""
    result = Ok(42)
    assert "Ok" in repr(result)
    assert "42" in repr(result)


def test_err_repr() -> None:
    """Test Err string representation."""
    result = Err("error")
    assert "Err" in repr(result)
    assert "error" in repr(result)


def test_result_equality() -> None:
    """Test Result instances equality."""
    assert Ok(42) == Ok(42)
    assert Err("test") == Err("test")
    assert Ok(42) != Err(42)
    assert Ok(42) != Ok(43)
