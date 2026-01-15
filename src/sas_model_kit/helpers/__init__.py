"""Helper utilities for SAS Model Kit.

This package provides capability-based protocol abstractions for framework-specific
operations. The design follows the Capability-Based Protocol Architecture (Phase 5)
to avoid God Object anti-patterns.

Key Components:
    - TypeVar T: Generic type bound to swat.CASTable for type safety
    - 8 Able Protocols: ReadAble, WriteAble, SortAble, DeleteAble, ConcatAble,
                        ValidateAble, ActionExecutable, ResultParseable
    - SWAT Implementation: SWATOperationsImpl class implementing all 8 Able protocols

Design Principles:
    - CSRP: Each Able has single responsibility (1-5 related methods)
    - ISP: Interface segregation - depend only on needed capabilities
    - DIP: Depend on abstractions (Protocols), not concrete implementations
    - Return Concrete Type: Methods return swat.CASTable, not Domain entities

Usage Example:
    >>> from sas_model_kit.helpers import T
    >>> from sas_model_kit.helpers.protocols import ValidateAble
    >>>
    >>> def check_table(validatable: ValidateAble, table: T) -> Result[T, TableNotFoundError]:
    ...     return validatable.ensure_exists(table)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

# TypeVar for type-safe CASTable operations
# Bound to swat.CASTable to ensure type safety across all Able protocols
# Defined at package-level for unified usage across helpers module
if TYPE_CHECKING:
    import swat

    T = TypeVar("T", bound=swat.CASTable)
else:
    # Runtime: Use Any to avoid hard dependency on swat
    from typing import Any

    T = TypeVar("T", bound=Any)


__all__ = [
    "T",
]
