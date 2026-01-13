"""Tests for SWATOperationAdapter actionset auto-loading feature."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from sas_model_kit.operation.swat import SWATOperationAdapter


class TestActionsetAutoLoading:
    """Test automatic actionset loading in SWATOperationAdapter."""

    def test_actionset_loaded_on_first_call(self) -> None:
        """Should auto-load actionset on first call_action."""
        # Arrange
        mock_session = MagicMock()
        mock_session.has_actionset.return_value = False
        mock_session.loadactionset.return_value = None

        # Mock the actionset and action
        mock_actionset = MagicMock()
        mock_action = MagicMock(return_value={"result": "success"})
        mock_actionset.score = mock_action
        mock_session.astore = mock_actionset

        with patch("sas_model_kit.operation.swat.isinstance", return_value=True):
            adapter = SWATOperationAdapter(mock_session)

            # Act
            result = adapter.call_action("astore.score", table="input")

            # Assert
            mock_session.loadactionset.assert_called_once_with("astore")
            mock_action.assert_called_once_with(table="input")
            assert result.is_ok
            assert result.value == {"result": "success"}
            assert adapter._loaded_actionsets == {"astore"}

    def test_actionset_not_reloaded_on_second_call(self) -> None:
        """Should not reload actionset on subsequent calls."""
        # Arrange
        mock_session = MagicMock()
        mock_session.has_actionset.return_value = True
        mock_session.loadactionset.return_value = None

        # Mock the actionset
        mock_actionset = MagicMock()
        mock_action = MagicMock(return_value={"result": "success"})
        mock_actionset.score = mock_action
        mock_session.astore = mock_actionset

        with patch("sas_model_kit.operation.swat.isinstance", return_value=True):
            adapter = SWATOperationAdapter(mock_session)

            # Act - First call
            adapter.call_action("astore.score", table="input1")
            second = adapter.call_action("astore.score", table="input2")

            # Assert - loadactionset called only once (or zero if has_actionset=True)
            assert mock_session.loadactionset.call_count <= 1
            assert "astore" in adapter._loaded_actionsets
            assert second.is_ok

    def test_multiple_actionsets_tracked_separately(self) -> None:
        """Should track multiple actionsets independently."""
        # Arrange
        mock_session = MagicMock()
        mock_session.has_actionset.return_value = False
        mock_session.loadactionset.return_value = None

        # Mock actionsets
        mock_astore = MagicMock()
        mock_astore.score = MagicMock(return_value={})
        mock_session.astore = mock_astore

        mock_explain = MagicMock()
        mock_explain.shapleyExplainer = MagicMock(return_value={})
        mock_session.explainModel = mock_explain

        with patch("sas_model_kit.operation.swat.isinstance", return_value=True):
            adapter = SWATOperationAdapter(mock_session)

            # Act
            result_one = adapter.call_action("astore.score", table="input")
            result_two = adapter.call_action(
                "explainModel.shapleyExplainer", data="train"
            )

            # Assert
            assert "astore" in adapter._loaded_actionsets
            assert "explainModel" in adapter._loaded_actionsets
            assert len(adapter._loaded_actionsets) == 2
            assert result_one.is_ok
            assert result_two.is_ok

    def test_actionset_already_on_server_not_reloaded(self) -> None:
        """Should not call loadactionset if server already has it."""
        # Arrange
        mock_session = MagicMock()
        mock_session.has_actionset.return_value = True  # Already loaded

        mock_actionset = MagicMock()
        mock_actionset.score = MagicMock(return_value={})
        mock_session.astore = mock_actionset

        with patch("sas_model_kit.operation.swat.isinstance", return_value=True):
            adapter = SWATOperationAdapter(mock_session)

            # Act
            result = adapter.call_action("astore.score", table="input")

            # Assert
            mock_session.loadactionset.assert_not_called()
            assert "astore" in adapter._loaded_actionsets
            assert result.is_ok

    def test_loadactionset_failure_graceful(self) -> None:
        """Should continue execution even if loadactionset fails."""
        # Arrange
        mock_session = MagicMock()
        mock_session.has_actionset.return_value = False
        mock_session.loadactionset.side_effect = Exception("Load failed")

        # Mock actionset (might already be loaded)
        mock_actionset = MagicMock()
        mock_actionset.score = MagicMock(return_value={"result": "ok"})
        mock_session.astore = mock_actionset

        with patch("sas_model_kit.operation.swat.isinstance", return_value=True):
            adapter = SWATOperationAdapter(mock_session)

            # Act - Should not raise during auto-load
            result = adapter.call_action("astore.score", table="input")

            # Assert - Execution continues
            assert "astore" in adapter._loaded_actionsets
            assert result.is_ok
            assert result.value == {"result": "ok"}

    def test_datastep_actionset_auto_loaded(self) -> None:
        """Should auto-load datastep actionset for runCode."""
        # Arrange
        mock_session = MagicMock()
        mock_session.has_actionset.return_value = False
        mock_session.loadactionset.return_value = None

        mock_datastep = MagicMock()
        mock_datastep.runCode = MagicMock(return_value={"success": True})
        mock_session.datastep = mock_datastep

        with patch("sas_model_kit.operation.swat.isinstance", return_value=True):
            adapter = SWATOperationAdapter(mock_session)

            # Act
            result = adapter.call_action("datastep.runCode", code="data x; run;")

            # Assert
            assert "datastep" in adapter._loaded_actionsets
            mock_datastep.runCode.assert_called_once()
            assert result.is_ok


class TestActionsetInitialization:
    """Test adapter initialization with actionset tracking."""

    def test_adapter_starts_with_empty_loaded_set(self) -> None:
        """Should start with no actionsets marked as loaded."""
        # Arrange
        mock_session = MagicMock()

        with patch("sas_model_kit.operation.swat.isinstance", return_value=True):
            # Act
            adapter = SWATOperationAdapter(mock_session)

            # Assert
            assert adapter._loaded_actionsets == set()
            assert len(adapter._loaded_actionsets) == 0

    def test_multiple_adapters_independent(self) -> None:
        """Should maintain independent actionset tracking per adapter."""
        # Arrange
        mock_session = MagicMock()
        mock_session.has_actionset.return_value = False

        mock_actionset = MagicMock()
        mock_actionset.score = MagicMock(return_value={})
        mock_session.astore = mock_actionset

        with patch("sas_model_kit.operation.swat.isinstance", return_value=True):
            adapter1 = SWATOperationAdapter(mock_session)
            adapter2 = SWATOperationAdapter(mock_session)

            # Act
            adapter1.call_action("astore.score", table="input")

            # Assert
            assert "astore" in adapter1._loaded_actionsets
            assert "astore" not in adapter2._loaded_actionsets
