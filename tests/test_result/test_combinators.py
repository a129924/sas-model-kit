"""Tests for Result combinator methods: and_then, map, map_err, or_else, unwrap_or_raise.

Combinators allow functional composition of Result-returning operations.
These tests validate method chaining, error handling, and type safety.
"""

import pytest

from sas_model_kit.result.base import Err, Ok, Result


class TestAndThen:
    """Tests for Result.and_then() - monadic bind operation."""

    def test_and_then_ok_applies_function(self) -> None:
        """Test and_then applies function when Ok."""

        def add_one(x: int) -> Result[int, str]:
            return Ok(x + 1)

        result = Ok(42).and_then(add_one)
        assert result.is_ok
        assert result.unwrap() == 43

    def test_and_then_ok_error_result(self) -> None:
        """Test and_then returns error result when function returns Err."""

        def fail(x: int) -> Result[int, str]:
            return Err("operation failed")

        result = Ok(42).and_then(fail)
        assert result.is_err
        assert result.error == "operation failed"

    def test_and_then_err_skips_function(self) -> None:
        """Test and_then skips function when Err."""

        def add_one(x: int) -> Result[int, str]:
            return Ok(x + 1)

        result = Err("initial error").and_then(add_one)
        assert result.is_err
        assert result.error == "initial error"

    def test_and_then_chaining(self) -> None:
        """Test chaining multiple and_then operations."""

        def add_one(x: int) -> Result[int, str]:
            return Ok(x + 1)

        def double(x: int) -> Result[int, str]:
            return Ok(x * 2)

        result = Ok(5).and_then(add_one).and_then(double)
        assert result.is_ok
        assert result.unwrap() == 12  # (5 + 1) * 2

    def test_and_then_stops_on_first_error(self) -> None:
        """Test chaining stops when first error occurs."""

        def step1(x: int) -> Result[int, str]:
            return Ok(x + 1)

        def step2(x: int) -> Result[int, str]:
            return Err("step2 failed")

        def step3(x: int) -> Result[int, str]:
            return Ok(x * 2)

        result = Ok(5).and_then(step1).and_then(step2).and_then(step3)
        assert result.is_err
        assert result.error == "step2 failed"

    def test_and_then_with_different_types(self) -> None:
        """Test and_then with type transformation."""

        def to_string(x: int) -> Result[str, str]:
            return Ok(f"value_{x}")

        result = Ok(42).and_then(to_string)
        assert result.is_ok
        assert result.unwrap() == "value_42"

    def test_and_then_with_complex_error_type(self) -> None:
        """Test and_then with complex error types."""

        def safe_divide(x: int) -> Result[int, dict]:
            return Ok(100 // x) if x != 0 else Err({"error": "divide by zero"})

        result = Ok(10).and_then(safe_divide)
        assert result.is_ok
        assert result.unwrap() == 10

        result = Ok(0).and_then(safe_divide)
        assert result.is_err
        assert result.error == {"error": "divide by zero"}


class TestMap:
    """Tests for Result.map() - transformation of success values."""

    def test_map_ok_transforms_value(self) -> None:
        """Test map transforms value when Ok."""
        result = Ok(42).map(lambda x: x * 2)
        assert result.is_ok
        assert result.unwrap() == 84

    def test_map_err_skips_transform(self) -> None:
        """Test map skips transformation when Err."""
        result = Err("error").map(lambda x: x * 2)
        assert result.is_err
        assert result.error == "error"

    def test_map_type_transformation(self) -> None:
        """Test map can transform to different type."""
        result = Ok(42).map(str)
        assert result.is_ok
        assert result.unwrap() == "42"

    def test_map_chaining(self) -> None:
        """Test chaining multiple map operations."""
        result = Ok(10).map(lambda x: x * 2).map(lambda x: x + 5).map(str)
        assert result.is_ok
        assert result.unwrap() == "25"

    def test_map_with_complex_transformation(self) -> None:
        """Test map with complex transformation function."""

        def format_data(x: int) -> dict:
            return {"value": x, "doubled": x * 2}

        result = Ok(42).map(format_data)
        assert result.is_ok
        assert result.unwrap() == {"value": 42, "doubled": 84}

    def test_map_with_none_value(self) -> None:
        """Test map works with None values."""
        result = Ok(None).map(lambda x: "transformed")
        assert result.is_ok
        assert result.unwrap() == "transformed"

    def test_map_preserves_ok_type_for_unchanged_result(self) -> None:
        """Test map preserves Ok type structure."""
        original = Ok(42)
        mapped = original.map(lambda x: x)
        assert mapped.is_ok
        assert isinstance(mapped, Ok)


class TestMapErr:
    """Tests for Result.map_err() - transformation of error values."""

    def test_map_err_transforms_error(self) -> None:
        """Test map_err transforms error when Err."""
        result = Err(ValueError("invalid")).map_err(str)
        assert result.is_err
        assert result.error == "invalid"

    def test_map_err_ok_skips_transform(self) -> None:
        """Test map_err skips transformation when Ok."""
        result = Ok(42).map_err(str)
        assert result.is_ok
        assert result.unwrap() == 42

    def test_map_err_error_type_change(self) -> None:
        """Test map_err can transform to different error type."""
        result = Err("simple error").map_err(lambda e: {"error": e, "code": 500})
        assert result.is_err
        assert result.error == {"error": "simple error", "code": 500}

    def test_map_err_chaining(self) -> None:
        """Test chaining multiple map_err operations."""
        result = (
            Err("original").map_err(lambda e: f"error_{e}").map_err(lambda e: e.upper())
        )
        assert result.is_err
        assert result.error == "ERROR_ORIGINAL"

    def test_map_err_normalizing_exception_to_string(self) -> None:
        """Test map_err normalizing exceptions to strings."""
        exception = ValueError("test error")
        result = Err(exception).map_err(lambda e: f"{type(e).__name__}: {str(e)}")
        assert result.is_err
        assert result.error == "ValueError: test error"

    def test_map_err_preserves_err_type_for_unchanged_result(self) -> None:
        """Test map_err preserves Err type structure."""
        original = Err("error")
        mapped = original.map_err(lambda e: e)
        assert mapped.is_err
        assert isinstance(mapped, Err)


class TestOrElse:
    """Tests for Result.or_else() - recovery from errors."""

    def test_or_else_ok_skips_recovery(self) -> None:
        """Test or_else skips recovery function when Ok."""

        def recover(e: str) -> Result[int, str]:
            return Ok(0)

        result = Ok(42).or_else(recover)
        assert result.is_ok
        assert result.unwrap() == 42

    def test_or_else_err_applies_recovery(self) -> None:
        """Test or_else applies recovery function when Err."""

        def recover(e: str) -> Result[int, str]:
            return Ok(0)

        result = Err("error").or_else(recover)
        assert result.is_ok
        assert result.unwrap() == 0

    def test_or_else_recovery_fails(self) -> None:
        """Test or_else when recovery also fails."""

        def recover(e: str) -> Result[int, str]:
            return Err(f"recovery failed: {e}")

        result = Err("initial error").or_else(recover)
        assert result.is_err
        assert result.error == "recovery failed: initial error"

    def test_or_else_chaining(self) -> None:
        """Test chaining multiple or_else for fallback logic."""

        def try_first(e: str) -> Result[int, str]:
            return Err("first attempt failed") if e == "x" else Ok(1)

        def try_second(e: str) -> Result[int, str]:
            return Ok(2)

        result = Err("x").or_else(try_first).or_else(try_second)
        assert result.is_ok
        assert result.unwrap() == 2

    def test_or_else_conditional_recovery(self) -> None:
        """Test or_else with conditional recovery logic."""

        def recover(e: str) -> Result[int, str]:
            if e == "recoverable":
                return Ok(42)
            return Err(f"unrecoverable: {e}")

        result1 = Err("recoverable").or_else(recover)
        assert result1.is_ok
        assert result1.unwrap() == 42

        result2 = Err("fatal").or_else(recover)
        assert result2.is_err

    def test_or_else_error_type_transformation(self) -> None:
        """Test or_else can transform error type during recovery."""

        def recover(e: str) -> Result[int, dict]:
            return Err({"original": e, "recovered": False})

        result = Err("failure").or_else(recover)
        assert result.is_err
        assert result.error == {"original": "failure", "recovered": False}


class TestUnwrapOrRaise:
    """Tests for Result.unwrap_or_raise() - explicit error raising."""

    def test_unwrap_or_raise_ok_returns_value(self) -> None:
        """Test unwrap_or_raise returns value when Ok."""
        result = Ok(42)
        assert result.unwrap_or_raise() == 42

    def test_unwrap_or_raise_err_with_exception(self) -> None:
        """Test unwrap_or_raise raises exception when Err."""
        result = Err(ValueError("test error"))
        with pytest.raises(ValueError, match="test error"):
            result.unwrap_or_raise()

    def test_unwrap_or_raise_err_with_string(self) -> None:
        """Test unwrap_or_raise raises RuntimeError for non-Exception error."""
        result = Err("string error")
        with pytest.raises(RuntimeError, match="Result is Err"):
            result.unwrap_or_raise()

    def test_unwrap_or_raise_is_alias_for_unwrap(self) -> None:
        """Test unwrap_or_raise behaves identically to unwrap."""
        ok_result = Ok(42)
        err_result = Err(ValueError("test"))

        assert ok_result.unwrap_or_raise() == ok_result.unwrap()

        with pytest.raises(ValueError):
            err_result.unwrap_or_raise()

        with pytest.raises(ValueError):
            err_result.unwrap()


class TestCombinatorIntegration:
    """Integration tests combining multiple combinators."""

    def test_and_then_with_map(self) -> None:
        """Test combining and_then and map."""

        def operation(x: int) -> Result[int, str]:
            return Ok(x * 2) if x > 0 else Err("negative")

        result = Ok(5).and_then(operation).map(lambda x: x + 1)
        assert result.is_ok
        assert result.unwrap() == 11

    def test_map_then_map_err(self) -> None:
        """Test map followed by map_err on error branch."""

        def validate(x: int) -> Result[int, str]:
            return Ok(x) if x > 0 else Err("not positive")

        result = Ok(-5).and_then(validate).map_err(lambda e: f"validation: {e}")
        assert result.is_err
        assert result.error == "validation: not positive"

    def test_or_else_with_and_then(self) -> None:
        """Test or_else providing Ok that chains with and_then."""

        def double(x: int) -> Result[int, str]:
            return Ok(x * 2)

        result = Err("initial").or_else(lambda _: Ok(10)).and_then(double)
        assert result.is_ok
        assert result.unwrap() == 20

    def test_complex_pipeline(self) -> None:
        """Test complex pipeline with multiple combinators."""

        def step1(x: int) -> Result[int, str]:
            return Ok(x + 1) if x >= 0 else Err("negative input")

        def step2(x: int) -> Result[str, str]:
            return Ok(f"value_{x}")

        result = (
            Ok(5)
            .and_then(step1)
            .and_then(step2)
            .map(lambda s: s.upper())
            .or_else(lambda _: Ok("DEFAULT"))
        )
        assert result.is_ok
        assert result.unwrap() == "VALUE_6"

    def test_error_recovery_pipeline(self) -> None:
        """Test error recovery with multiple strategies."""

        def try_parse_int(s: str) -> Result[int, str]:
            try:
                return Ok(int(s))
            except ValueError:
                return Err(f"cannot parse: {s}")

        result = (
            try_parse_int("invalid")
            .or_else(lambda _: try_parse_int("42"))
            .map(lambda x: x * 2)
        )
        assert result.is_ok
        assert result.unwrap() == 84

    def test_map_err_for_error_context_enrichment(self) -> None:
        """Test using map_err to enrich error context."""

        def operation() -> Result[int, str]:
            return Err("operation failed")

        result = operation().map_err(
            lambda e: {"error": e, "context": "processing", "retry_count": 0}
        )
        assert result.is_err
        assert result.error["context"] == "processing"

    def test_match_case_with_union_type(self) -> None:
        """Test pattern matching on Result types."""

        def operation(x: int) -> Result[int, str | int]:
            if x < 0:
                return Err("negative")
            if x == 0:
                return Err(42)
            return Ok(x * 2)

        result = operation(5)
        match result:
            case Ok(value):
                assert value == 10
            case Err(_):
                pytest.fail("Should be Ok")

        result_err = operation(-1)
        match result_err:
            case Err(error):
                assert error == "negative"
            case Ok(_):
                pytest.fail("Should be Err")
