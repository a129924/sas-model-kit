"""Tests for ModelResult generic container."""

from sas_model_kit.result import ModelResult, ResultStatus, StreamableResult


class MockStreamable(StreamableResult):
    """Mock StreamableResult for testing."""

    def __iter__(self):
        """Iterate over mock data."""
        return iter([{"id": 1}, {"id": 2}])

    def stream(self, batch_size: int = 1000):
        """Stream mock data."""
        return iter([{"id": 1}, {"id": 2}])

    def to_records(self) -> list[dict]:
        """Convert to records."""
        return [{"id": 1}, {"id": 2}]


def test_model_result_with_success_status() -> None:
    """Test creating a successful ModelResult."""
    data = {"result": "success"}
    result = ModelResult(
        status=ResultStatus.SUCCESS,
        data=data,
        metadata={"rows": 100},
    )

    assert result.status == ResultStatus.SUCCESS
    assert result.data == data
    assert result.metadata == {"rows": 100}


def test_model_result_with_error_status() -> None:
    """Test creating an error ModelResult."""
    result = ModelResult(
        status=ResultStatus.ERROR,
        data=None,
        metadata={"error": "Connection failed"},
    )

    assert result.status == ResultStatus.ERROR
    assert result.data is None
    assert result.metadata["error"] == "Connection failed"


def test_model_result_with_streamable_data() -> None:
    """Test ModelResult with StreamableResult data."""
    streamable = MockStreamable()
    result = ModelResult(
        status=ResultStatus.SUCCESS,
        data=streamable,
    )

    assert result.status == ResultStatus.SUCCESS
    assert isinstance(result.data, StreamableResult)


def test_model_result_is_success_property() -> None:
    """Test is_success convenience property."""
    success_result = ModelResult(
        status=ResultStatus.SUCCESS,
        data="data",
    )
    error_result = ModelResult(
        status=ResultStatus.ERROR,
        data=None,
    )

    assert success_result.is_success is True
    assert error_result.is_success is False


def test_model_result_is_error_property() -> None:
    """Test is_error convenience property."""
    success_result = ModelResult(
        status=ResultStatus.SUCCESS,
        data="data",
    )
    error_result = ModelResult(
        status=ResultStatus.ERROR,
        data=None,
    )

    assert success_result.is_error is False
    assert error_result.is_error is True


def test_model_result_default_metadata() -> None:
    """Test that metadata defaults to empty dict."""
    result = ModelResult(
        status=ResultStatus.SUCCESS,
        data="data",
    )

    assert result.metadata == {}


def test_model_result_metadata_immutability() -> None:
    """Test that metadata can be modified after creation."""
    result = ModelResult(
        status=ResultStatus.SUCCESS,
        data="data",
        metadata={"initial": "value"},
    )

    result.metadata["new"] = "data"

    assert result.metadata["new"] == "data"
    assert result.metadata["initial"] == "value"


def test_model_result_generic_type_int() -> None:
    """Test ModelResult with int generic type."""
    result: ModelResult[int] = ModelResult(
        status=ResultStatus.SUCCESS,
        data=42,
    )

    assert result.data == 42
    assert isinstance(result.data, int)


def test_model_result_generic_type_list() -> None:
    """Test ModelResult with list generic type."""
    data = [1, 2, 3, 4, 5]
    result: ModelResult[list[int]] = ModelResult(
        status=ResultStatus.SUCCESS,
        data=data,
    )

    assert result.data == data
    assert isinstance(result.data, list)


def test_model_result_generic_type_dict() -> None:
    """Test ModelResult with dict generic type."""
    data = {"key": "value", "number": 123}
    result: ModelResult[dict] = ModelResult(
        status=ResultStatus.SUCCESS,
        data=data,
    )

    assert result.data == data
    assert isinstance(result.data, dict)
