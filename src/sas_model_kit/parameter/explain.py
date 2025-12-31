"""Explain model parameter for model explainability analysis.

This module provides parameters for generating model explanations,
including Shapley value computation configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from typing_extensions import override

from .base import BaseModelParameter


@dataclass(frozen=True)
class ExplainParameter(BaseModelParameter):
    """Parameters for model explainability analysis via Shapley values.

    Extends BaseModelParameter with explanation-specific configuration
    for Shapley value computation on SAS Viya models.

    Attributes:
        source_caslib: Source data CAS library
        source_table: Source data CAS table
        target_caslib: Target output CAS library
        target_table: Target output CAS table
        train_table: Training data CAS table name for Shapley computation
        train_caslib: Training data CAS library
        predicted_target: Target variable name for explanation
        features: List of feature column names for Shapley calculation
        id_cols: Set of ID column names to identify unique records
        depth: Shapley explanation depth (controls calculation complexity, typically 1-10)
        sas_score_code: Optional SAS evaluation code for data preprocessing

    Examples:
        >>> param = ExplainParameter(
        ...     source_caslib="public",
        ...     source_table="test_data",
        ...     target_caslib="public",
        ...     target_table="explanations",
        ...     train_table="training_data",
        ...     train_caslib="public",
        ...     predicted_target="churn_pred",
        ...     features=["age", "income", "tenure"],
        ...     id_cols={"customer_id"},
        ...     depth=2,
        ... )
        >>> param.validate()
    """

    train_table: str
    train_caslib: str
    predicted_target: str
    features: list[str]
    id_cols: set[str]
    depth: int
    sas_score_code: str | None = None

    @override
    def validate(self) -> None:
        """Validate explain parameter values.

        Raises:
            ValueError: If required parameters are invalid

        Note:
            Validates base parameters first, then explanation-specific fields.
        """
        super().validate()

        if not self.train_table:
            msg = "train_table cannot be empty"
            raise ValueError(msg)

        if not self.train_caslib:
            msg = "train_caslib cannot be empty"
            raise ValueError(msg)

        if not self.predicted_target:
            msg = "predicted_target cannot be empty"
            raise ValueError(msg)

        if not self.features:
            msg = "features cannot be empty"
            raise ValueError(msg)

        if not isinstance(self.features, list):
            msg = f"features must be a list, got {type(self.features)}"
            raise ValueError(msg)

        if not self.id_cols:
            msg = "id_cols cannot be empty"
            raise ValueError(msg)

        if not isinstance(self.id_cols, set):
            msg = f"id_cols must be a set, got {type(self.id_cols)}"
            raise ValueError(msg)

        if not isinstance(self.depth, int) or self.depth < 1:
            msg = f"depth must be a positive int, got {self.depth}"
            raise ValueError(msg)
