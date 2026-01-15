"""SWAT-specific type definitions for helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    import swat

    SwatTableT = TypeVar("SwatTableT", bound=swat.CASTable)
else:
    SwatTableT = TypeVar("SwatTableT", bound=Any)


__all__ = ["SwatTableT"]
