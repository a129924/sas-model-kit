"""
Unit tests for ResultStatus.

Tests verify that ResultStatus enum is correctly defined with
expected values and behavior.
"""

from sas_model_kit.result.status import ResultStatus


class TestResultStatus:
    """Test ResultStatus enum."""

    def test_success_value(self):
        """Should have SUCCESS with 'success' value."""
        assert ResultStatus.SUCCESS.value == "success"

    def test_error_value(self):
        """Should have ERROR with 'error' value."""
        assert ResultStatus.ERROR.value == "error"

    def test_only_two_statuses(self):
        """Should only have SUCCESS and ERROR statuses."""
        assert len(ResultStatus) == 2

    def test_success_equality(self):
        """Should support equality comparison."""
        status = ResultStatus.SUCCESS
        assert status == ResultStatus.SUCCESS
        assert status != ResultStatus.ERROR

    def test_string_representation(self):
        """Should have string representation."""
        assert str(ResultStatus.SUCCESS) == "ResultStatus.SUCCESS"
        assert str(ResultStatus.ERROR) == "ResultStatus.ERROR"
