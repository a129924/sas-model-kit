"""Explain model parameter for model explainability analysis.

This module provides parameters for generating model explanations
via Shapley value computation, supporting both ASTORE and DataStep models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from typing_extensions import override

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
                 CRITICAL: SWAT uses this to map results back to original records
        depth: Shapley explanation depth (REQUIRED, >= 1, typically 1-10)
        model_caslib: ASTORE model library (OPTIONAL - must have model_table if present)
        model_table: ASTORE model table (OPTIONAL - must have model_caslib if present)
        sas_score_code: DataStep preprocessing code (OPTIONAL)
        casout: Optional CAS output configuration dict. If None, framework auto-generates
               with default settings. Supports keys: {name, caslib, replace, promote, backup}

    Validation Rules:
        - train_caslib, train_table: always required
        - score_caslib, score_table: both required or both None
        - predicted_target, features, id_cols, depth: always required
        - At least one model must be provided: (model_caslib+model_table) OR sas_score_code

    Examples:
        >>> # Minimal: ASTORE model, auto-generated output
        >>> param = ExplainParameter(
        ...     train_caslib="public",
        ...     train_table="training_data",
        ...     predicted_target="churn_pred",
        ...     features=["age", "income", "tenure"],
        ...     id_cols={"customer_id"},
        ...     depth=1,
        ...     model_caslib="models",
        ...     model_table="my_astore",
        ... )
        >>> param.validate()

        >>> # With scoring data and DataStep preprocessing
        >>> param_complex = ExplainParameter(
        ...     train_caslib="public",
        ...     train_table="training_data",
        ...     score_caslib="public",
        ...     score_table="test_data",
        ...     predicted_target="churn_pred",
        ...     features=["age", "income", "tenure"],
        ...     id_cols={"customer_id"},
        ...     depth=2,
        ...     model_caslib="models",
        ...     model_table="my_astore",
        ...     sas_score_code="new_var = var1 + var2;",
        ...     casout={"name": "explain_results", "promote": True}
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

    # Scoring layer (optional - must be paired)
    score_caslib: str | None = None
    score_table: str | None = None

    # Model definition (one required: ASTORE or DataStep)
    model_caslib: str | None = None
    model_table: str | None = None
    sas_score_code: str | None = None

    # Output configuration (optional)
    casout: dict[str, Any] | None = None

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

        # Validate model definition structure
        # If ASTORE fields are provided, both must exist and be non-empty
        if (self.model_caslib is not None or self.model_table is not None) and not (
            self.model_caslib and self.model_table
        ):
            msg = "model_caslib and model_table must both be provided or both be None"
            raise ValueError(msg)

        # Validate that at least one model is provided
        has_astore = (
            self.model_caslib is not None
            and self.model_caslib
            and self.model_table is not None
            and self.model_table
        )
        has_datastep = self.sas_score_code is not None and self.sas_score_code

        if not (has_astore or has_datastep):
            msg = (
                "At least one model must be provided: "
                "(model_caslib + model_table) for ASTORE or "
                "sas_score_code for DataStep"
            )
            raise ValueError(msg)

        # Validate casout if provided
        if self.casout is not None:
            if not isinstance(self.casout, dict):
                msg = "casout must be a dictionary or None"
                raise ValueError(msg)
            if "name" not in self.casout or not self.casout["name"]:
                msg = "casout['name'] is required when casout is provided"
                raise ValueError(msg)
