"""Mapper layer base classes and protocols.

This module provides abstract base classes and protocols for parameter mapping,
converting domain parameters to backend-specific dictionary formats.

Design:
    - Parameter mappers convert Parameter objects to backend action dicts
    - Each backend (SWAT, SASCTL, HTTPx) has separate mappers
    - Mappers follow SRP (Single Responsibility Principle)
    - Executor layer holds mapper instances

Protocols:
    - ParameterMapper[P]: Base protocol for parameter mapping

Examples:
    >>> from sas_model_kit.model.parameter import AstoreParameter
    >>> from sas_model_kit.model.mapper.swat import AstoreParameterToSwatDictMapper
    >>>
    >>> param = AstoreParameter(...)
    >>> mapper = AstoreParameterToSwatDictMapper()
    >>> action_dict = mapper.map(param, **context)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

P = TypeVar("P")  # Parameter type


class ParameterMapper(ABC, Generic[P]):
    """Abstract base class for parameter mappers.

    Mappers convert domain Parameter objects to backend-specific
    action parameter dictionaries. Each mapper is responsible for
    a single parameter type and backend combination.

    Type Parameters:
        P: The Parameter type to map (e.g., AstoreParameter)

    Design Notes:
        - Pure transformation (no side effects)
        - Stateless (no instance variables)
        - Backend-specific (knows SWAT/SASCTL/HTTPx details)
        - Parameter-specific (handles one parameter type)

    Examples:
        >>> class MyParameterMapper(ParameterMapper[MyParameter]):
        ...     def map(self, parameter, **context):
        ...         return {
        ...             "field1": parameter.value1,
        ...             "field2": parameter.value2,
        ...         }
    """

    @abstractmethod
    def map(self, parameter: P, **context: Any) -> dict[str, Any]:
        """Map parameter to backend action dictionary.

        Converts a domain Parameter object into a backend-specific
        dictionary suitable for action invocation.

        Args:
            parameter: Domain parameter object
            **context: Runtime context (where conditions, output locations, etc.)

        Returns:
            Dictionary with backend-specific action parameters

        Raises:
            ValueError: If parameter is invalid or required context missing

        Examples:
            >>> mapper = AstoreParameterToSwatDictMapper()
            >>> action_dict = mapper.map(
            ...     astore_param,
            ...     where_condition="id=123"
            ... )
        """
        ...
