"""Explain model parameter for model explainability analysis.

This module provides parameters for generating model explanations
via Shapley value computation, supporting both ASTORE and DataStep models.
"""

from __future__ import annotations

from dataclasses import dataclass

from typing_extensions import override

from sas_model_kit.model.types import ModelTableType

from .base import BaseModelParameter


@dataclass(frozen=True)
class ExplainParameter(BaseModelParameter):
    """Parameters for model explainability analysis via Shapley values.

    Combines training data, optional scoring data, and model configuration
    to compute Shapley-based feature importance explanations.

    Three-layer design:
    1. Training layer (required): train_caslib, train_table
    2. Scoring layer (optional): score_caslib, score_table (if provided, must both exist)
    3. Model definition (one required): either ASTORE (model_caslib/model_table) or DataStep (sas_score_code)

    Note: id_cols is critical for SWAT to keep result linked to original data via ID columns.

    Attributes:
        train_caslib: Training data CAS library (REQUIRED)
        train_table: Training data CAS table (REQUIRED)
        score_caslib: Scoring data CAS library (OPTIONAL - must have score_table if present)
        score_table: Scoring data CAS table (OPTIONAL - must have score_caslib if present)
        predicted_target: Target/prediction variable name for explanation (REQUIRED)
        features: List of feature column names for Shapley calculation (REQUIRED, non-empty)
        id_cols: Set of ID column names to preserve in results (REQUIRED, non-empty)
        depth: Shapley explanation depth (REQUIRED, >= 1, typically 1-10)
        model_table_type: Model type (REQUIRED: ASTORE or DATASTEP)
        model_caslib: ASTORE model library (REQUIRED if model_table_type=ASTORE)
        model_table: ASTORE model table (REQUIRED if model_table_type=ASTORE)
        sas_score_code: DataStep code (REQUIRED if model_table_type=DATASTEP)

    Validation Rules:
        - train_caslib, train_table: always required
        - score_caslib, score_table: both required or both None
        - predicted_target, features, id_cols, depth: always required
        - model_table_type: must be specified (ASTORE or DATASTEP)
        - If model_table_type=ASTORE: model_caslib + model_table required
        - If model_table_type=DATASTEP: sas_score_code required

    Examples:
        >>> # ASTORE model
        >>> param = ExplainParameter(
        ...     train_caslib="public",
        ...     train_table="training_data",
        ...     predicted_target="churn_pred",
        ...     features=["age", "income", "tenure"],
        ...     id_cols={"customer_id"},
        ...     depth=1,
        ...     model_table_type=ModelTableType.ASTORE,
        ...     model_caslib="models",
        ...     model_table="my_astore",
        ... )
        >>> param.validate()

        >>> # DataStep model with scoring data
        >>> param_datastep = ExplainParameter(
        ...     train_caslib="public",
        ...     train_table="training_data",
        ...     score_caslib="public",
        ...     score_table="test_data",
        ...     predicted_target="churn_pred",
        ...     features=["age", "income", "tenure"],
        ...     id_cols={"customer_id"},
        ...     depth=2,
        ...     model_table_type=ModelTableType.DATASTEP,
        ...     sas_score_code="y = a*x1 + b*x2;",
        ... )
    """

    # Training layer (required)
    train_caslib: str
    train_table: str

    # Explanation configuration (required)
    predicted_target: str
    features: list[str]
    id_cols: set[str]
    depth: int
    model_table_type: ModelTableType

    # Scoring layer (optional - must be paired)
    score_caslib: str | None = None
    score_table: str | None = None

    # Model definition (required: specify type and matching implementation)
    model_caslib: str | None = None  # Required if model_table_type=ASTORE
    model_table: str | None = None  # Required if model_table_type=ASTORE
    sas_score_code: str | None = None  # Required if model_table_type=DATASTEP

    @override
    def validate(self) -> None:
        """Validate explain parameter values.

        Raises:
            ValueError: If required parameters are invalid or constraint violated
        """
        # Validate training layer (always required)
        if not self.train_caslib:
            msg = "train_caslib cannot be empty"
            raise ValueError(msg)
        if not self.train_table:
            msg = "train_table cannot be empty"
            raise ValueError(msg)

        # Validate scoring layer (must be paired)
        has_score_caslib = self.score_caslib is not None and bool(self.score_caslib)
        has_score_table = self.score_table is not None and bool(self.score_table)

        if has_score_caslib != has_score_table:
            msg = "score_caslib and score_table must both be provided or both be None"
            raise ValueError(msg)

        # Validate explanation configuration (always required)
        if not self.predicted_target:
            msg = "predicted_target cannot be empty"
            raise ValueError(msg)

        if not self.features or not isinstance(self.features, (list, tuple)):
            msg = "features must be a non-empty list"
            raise ValueError(msg)

        if not self.id_cols or not isinstance(self.id_cols, set):
            msg = "id_cols must be a non-empty set"
            raise ValueError(msg)

        if not isinstance(self.depth, int) or self.depth < 1:
            msg = f"depth must be a positive integer, got {self.depth}"
            raise ValueError(msg)

        # Validate model definition - type-specific validation
        if self.model_table_type == ModelTableType.ASTORE:
            if not self.model_caslib or not self.model_table:
                msg = (
                    "For ASTORE model type, "
                    "both model_caslib and model_table must be provided"
                )
                raise ValueError(msg)
            if self.sas_score_code:
                msg = "For ASTORE model type, sas_score_code should not be provided"
                raise ValueError(msg)

        elif self.model_table_type == ModelTableType.DATASTEP:
            if not self.sas_score_code:
                msg = "For DATASTEP model type, sas_score_code is required"
                raise ValueError(msg)
            if self.model_caslib or self.model_table:
                msg = (
                    "For DATASTEP model type, "
                    "model_caslib and model_table should not be provided"
                )
                raise ValueError(msg)
        else:
            msg = f"Invalid model_table_type: {self.model_table_type}"
            raise ValueError(msg)
