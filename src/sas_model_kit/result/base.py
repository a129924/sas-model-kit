"""Rust-style Result base classes.

This module provides Rust-inspired Result types for type-safe error handling.
Following the principle of "explicit over implicit", this design makes success
and failure cases explicit in type signatures.

Design Philosophy:
    - Ok[T]: Represents successful computation with value T
    - Err[E]: Represents failed computation with error E
    - Result[T, E]: Union type that can be either Ok or Err
    - Explicit error handling without swallowing exceptions

Examples:
    >>> # Success case
    >>> result = Ok(42)
    >>> if result.is_ok:
    ...     print(result.unwrap())  # 42

    >>> # Failure case
    >>> result = Err(ValueError("invalid"))
    >>> if result.is_err:
    ...     print(result.error)  # ValueError("invalid")

    >>> # Safe unwrapping
    >>> value = result.unwrap_or(0)  # Returns 0 if error
"""

from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

T_co = TypeVar("T_co", covariant=True)
E_co = TypeVar("E_co", covariant=False)


class Result(ABC, Generic[T_co, E_co]):
    """Rust-style Result base class.

    Abstract base class for all Result types, providing unified success/failure
    checking and value extraction methods.

    Follows CSRP (Concrete Single Responsibility Principle):
    - Ok: Responsible for success results
    - Err: Responsible for failure results

    Type Parameters:
        T_co: Type of success value (covariant)
        E_co: Type of error value (covariant)

    Methods:
        is_ok: Check if result is Ok
        is_err: Check if result is Err
        unwrap(): Extract value or raise exception
        unwrap_or(default): Extract value or return default
        unwrap_or_else(fn): Extract value or compute default

    Examples:
        >>> result: Result[int, str] = Ok(42)
        >>> if result.is_ok:
        ...     print(result.unwrap())  # 42

        >>> result: Result[int, str] = Err("failed")
        >>> if result.is_err:
        ...     print(result.error)  # "failed"
    """

    @property
    def is_ok(self) -> bool:
        """Check if this is a success result.

        Returns:
            True if this is an Ok instance, False otherwise

        Examples:
            >>> Ok(42).is_ok
            True
            >>> Err("error").is_ok
            False
        """
        return isinstance(self, Ok)

    @property
    def is_err(self) -> bool:
        """Check if this is a failure result.

        Returns:
            True if this is an Err instance, False otherwise

        Examples:
            >>> Ok(42).is_err
            False
            >>> Err("error").is_err
            True
        """
        return isinstance(self, Err)

    def unwrap(self) -> T_co:
        """Extract the success value or raise exception.

        If this is an Ok, returns the contained value.
        If this is an Err, raises the contained error if it's an Exception,
        or raises RuntimeError with the error value.

        Returns:
            The success value if Ok

        Raises:
            Exception: The contained error if Err and error is an Exception
            RuntimeError: If Err and error is not an Exception

        Examples:
            >>> Ok(42).unwrap()
            42
            >>> Err(ValueError("test")).unwrap()
            Traceback (most recent call last):
                ...
            ValueError: test
        """
        if isinstance(self, Ok):
            return self.value
        # self is Err
        error = self.error  # type: ignore[attr-defined]
        if isinstance(error, Exception):
            raise error
        raise RuntimeError(f"Result is Err: {error}")

    def unwrap_or(self, default: T_co) -> T_co:  # type: ignore
        """Extract the success value or return default.

        If this is an Ok, returns the contained value.
        If this is an Err, returns the provided default value.

        Args:
            default: Value to return if this is Err

        Returns:
            The success value if Ok, default value if Err

        Examples:
            >>> Ok(42).unwrap_or(0)
            42
            >>> Err("error").unwrap_or(0)
            0
        """
        return self.value if isinstance(self, Ok) else default  # type: ignore[attr-defined]

    def unwrap_or_else(self, fn: Callable[[E_co], T_co]) -> T_co:
        """Extract the success value or compute default from error.

        If this is an Ok, returns the contained value.
        If this is an Err, calls the provided function with the error
        and returns the result.

        Args:
            fn: Function to compute default value from error

        Returns:
            The success value if Ok, computed value if Err

        Examples:
            >>> Ok(42).unwrap_or_else(lambda e: 0)
            42
            >>> Err("error").unwrap_or_else(lambda e: len(e))
            5
        """
        if isinstance(self, Ok):
            return self.value  # type: ignore[attr-defined]
        return fn(self.error)  # type: ignore[attr-defined]


@dataclass(frozen=True)
class Ok(Result[T_co, E_co], Generic[T_co, E_co]):
    """Success result containing a value.

    Represents a successful computation. Follows SRP (Single Responsibility
    Principle) - only responsible for holding success values.

    Attributes:
        value: The success value

    Examples:
        >>> result = Ok(42)
        >>> assert result.is_ok
        >>> assert result.unwrap() == 42

        >>> # Type-safe success
        >>> result: Result[int, str] = Ok(100)
        >>> if result.is_ok:
        ...     value: int = result.unwrap()
    """

    value: T_co


@dataclass(frozen=True)
class Err(Result[T_co, E_co], Generic[T_co, E_co]):
    """Failure result containing an error.

    Represents a failed computation. Follows SRP (Single Responsibility
    Principle) - only responsible for holding error values.

    Attributes:
        error: The error value

    Examples:
        >>> result = Err(ValueError("invalid"))
        >>> assert result.is_err
        >>> try:
        ...     result.unwrap()
        ... except ValueError as e:
        ...     print(str(e))  # "invalid"

        >>> # Type-safe failure
        >>> result: Result[int, ValueError] = Err(ValueError("test"))
        >>> if result.is_err:
        ...     error: ValueError = result.error
    """

    error: E_co
