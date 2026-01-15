"""Helper utilities for SAS Model Kit.

This package provides capability-based protocol abstractions for framework-specific
operations. The design follows the Capability-Based Protocol Architecture (Phase 5)
to avoid God Object anti-patterns.

Key Components:
    - 8 Able Protocols: ReadAble, WriteAble, SortAble, DeleteAble, ConcatAble,
                        ValidateAble, ActionExecutable, ResultParseable
    - SWAT Implementation: SWAT-specific helpers in helpers/swat/

Design Principles:
    - CSRP: Each Able has single responsibility (1-5 related methods)
    - ISP: Interface segregation - depend only on needed capabilities
    - DIP: Depend on abstractions (Protocols), not concrete implementations
    - Return Concrete Type: Methods return framework concrete types, not Domain entities

Usage Example:
    >>> from sas_model_kit.helpers.protocols import ValidateAble
    >>>
    >>> def check_table(validatable: ValidateAble, table):
    ...     return validatable.ensure_exists(table)
"""

from __future__ import annotations

__all__ = []
