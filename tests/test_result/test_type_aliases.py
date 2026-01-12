"""Smoke tests for public Result aliases and error exports."""

from sas_model_kit import result as result_mod


def test_operation_result_alias_exists() -> None:
    assert hasattr(result_mod, "OperationResult")
    assert hasattr(result_mod, "UploadResult")
    assert hasattr(result_mod, "FetchResult")


def test_transformation_aliases_exist() -> None:
    assert hasattr(result_mod, "TransformationExecutionResult")
    assert hasattr(result_mod, "SortExecutionResult")
    assert hasattr(result_mod, "UniqueKeyExecutionResult")


def test_validation_alias_exists() -> None:
    assert hasattr(result_mod, "ValidationResult")


def test_error_exports_available() -> None:
    for name in [
        "OperationError",
        "UploadFailure",
        "DataFetchFailure",
        "TransformationFailure",
        "InvalidColumnFailure",
        "SortError",
        "DuplicateKeyError",
        "ValidationFailure",
        "MissingFieldFailure",
        "InvalidTypeFailure",
        "ConflictingRuleFailure",
    ]:
        assert hasattr(result_mod, name)
