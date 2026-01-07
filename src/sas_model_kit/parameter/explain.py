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

    Combines training data and model configuration to compute Shapley-based
    feature importance explanations.

    Three-layer design:
    1. Training layer (required): train_caslib, train_table
    2. Explanation config (required): predicted_target, features, id_cols, depth, model_table_type
    3. Model definition (always required): model_caslib, model_table, sas_score_code

    Note: id_cols is critical for SWAT to keep result linked to original data via ID columns.

    Attributes:
        train_caslib: Training data CAS library (REQUIRED)
        train_table: Training data CAS table (REQUIRED)
        predicted_target: Target/prediction variable name for explanation (REQUIRED)
        features: List of feature column names for Shapley calculation (REQUIRED, non-empty)
        id_cols: Set of ID column names to preserve in results (REQUIRED, non-empty)
        depth: Shapley explanation depth (REQUIRED, >= 1, typically 1-10)
        model_table_type: Model type (REQUIRED: ASTORE or DATASTEP)
        model_caslib: Model location library (REQUIRED - where model is stored)
        model_table: Model location table (REQUIRED - where model is stored)
        sas_score_code: DS2/SAS code for scoring (REQUIRED - needed by SWAT)

    Validation Rules:
        - train_caslib, train_table: always required
        - predicted_target, features, id_cols, depth: always required
        - model_table_type: must be specified (ASTORE or DATASTEP)
        - model_caslib, model_table, sas_score_code: ALWAYS required (no exceptions)

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
        ...     sas_score_code="dcl package astore; ..."
        ... )
        >>> param.validate()

        >>> # DataStep model
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

    # Model definition (REQUIRED - both fields always required)
    model_caslib: str  # Always required (for model location or ASTORE reference)
    model_table: str  # Always required (for model location or ASTORE reference)
    sas_score_code: str  # Always required (DS2 code for scoring)

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

        # Validate model definition (ALWAYS required - all three fields)
        if not self.model_caslib:
            msg = "model_caslib is required"
            raise ValueError(msg)

        if not self.model_table:
            msg = "model_table is required"
            raise ValueError(msg)

        if not self.sas_score_code:
            msg = "sas_score_code is required"
            raise ValueError(msg)

        # Validate model_table_type matches usage
        if self.model_table_type == ModelTableType.ASTORE:
            # ASTORE uses model_caslib/model_table to locate the astore model
            pass
        elif self.model_table_type == ModelTableType.DATASTEP:
            # DATASTEP uses sas_score_code for inline scoring
            pass
        else:
            msg = f"Invalid model_table_type: {self.model_table_type}"
            raise ValueError(msg)
