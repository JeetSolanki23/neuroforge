from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from neuroforge.workflows.persistence import (
    _get_vault_state_path,
    load_project_state,
    save_project_state,
)


@patch("neuroforge.workflows.persistence.init_chroma")
@patch("neuroforge.workflows.persistence.get_collection")
def test_save_project_state_writes_vault_file(mock_get_coll, mock_init, tmp_path):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}
    mock_get_coll.return_value = mock_coll

    with patch("neuroforge.workflows.persistence.config") as mock_config:
        mock_config.MEMORY_VAULT_PATH = str(tmp_path)
        state = {
            "project_id": "p1",
            "raw_goal": "goal",
            "current_phase": "briefing",
        }

        res = save_project_state(state)
        assert res is True
        vault_file = tmp_path / "projects" / "p1" / "state.json"
        assert vault_file.exists()
        saved = json.loads(vault_file.read_text(encoding="utf-8"))
        assert saved["project_id"] == "p1"


@patch("neuroforge.workflows.persistence.init_chroma")
@patch("neuroforge.workflows.persistence.get_collection")
def test_load_project_state_reads_vault_file(mock_get_coll, mock_init, tmp_path):
    vault_file = tmp_path / "projects" / "p1" / "state.json"
    vault_file.parent.mkdir(parents=True, exist_ok=True)
    saved_state = {"project_id": "p1", "raw_goal": "build AI"}
    vault_file.write_text(json.dumps(saved_state), encoding="utf-8")

    mock_coll = MagicMock()
    mock_coll.get.return_value = {
        "ids": ["p1"],
        "metadatas": [{"vault_path": str(vault_file)}],
    }
    mock_get_coll.return_value = mock_coll

    res = load_project_state("p1")
    assert res == saved_state


@patch("neuroforge.workflows.persistence.init_chroma")
@patch("neuroforge.workflows.persistence.get_collection")
def test_load_project_state_returns_none_missing_vault(mock_get_coll, mock_init, tmp_path):
    missing_file = tmp_path / "projects" / "p1" / "state.json"

    mock_coll = MagicMock()
    mock_coll.get.return_value = {
        "ids": ["p1"],
        "metadatas": [{"vault_path": str(missing_file)}],
    }
    mock_get_coll.return_value = mock_coll

    res = load_project_state("p1")
    assert res is None


def test_get_vault_state_path_creates_dirs(tmp_path):
    with patch("neuroforge.workflows.persistence.config") as mock_config:
        mock_config.MEMORY_VAULT_PATH = str(tmp_path)
        path = _get_vault_state_path("p_test")
        assert path.parent.exists()
        assert path.name == "state.json"
