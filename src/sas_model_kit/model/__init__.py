"""
Model layer for SAS Model Kit.

This module provides abstract and concrete model classes for synchronous
model execution, following the Class Single Responsibility Principle (CSRP).

Architecture:
    - sync_model.py: SyncModel[ParameterT, PayloadT] ABC
    - concrete/: Concrete model implementations (ExplainModel, AstoreModel, DataStepModel)
    - executor/: Executor layer for backend-specific execution
    - payloads.py: Payload data types
"""

from sas_model_kit.model.concrete import AstoreModel, DataStepModel, ExplainModel
from sas_model_kit.model.sync_model import SyncModel

__all__ = [
    "SyncModel",
    "AstoreModel",
    "DataStepModel",
    "ExplainModel",
]
