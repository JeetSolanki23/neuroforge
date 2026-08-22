from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from neuroforge.workflows.persistence import (
    list_projects,
    load_project_state,
    save_project_state,
    update_task_status,
)


@patch("neuroforge.workflows.persistence.init_chroma")
@patch("neuroforge.workflows.persistence.get_collection")
def test_save_project_state_success(mock_get_coll, mock_init):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}
    mock_get_coll.return_value = mock_coll

    state = {
        "project_id": "p1",
        "raw_goal": "goal",
        "current_phase": "briefing",
        "team_approved": False,
        "needs_human_input": False,
        "tasks": [],
        "completed_task_ids": [],
        "failed_task_ids": [],
    }

    res = save_project_state(state)
    assert res is True
    mock_coll.add.assert_called_once()


@patch("neuroforge.workflows.persistence.init_chroma")
@patch("neuroforge.workflows.persistence.get_collection")
def test_save_project_state_upserts_existing(mock_get_coll, mock_init):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": ["p1"]}
    mock_get_coll.return_value = mock_coll

    state = {
        "project_id": "p1",
        "raw_goal": "goal",
        "current_phase": "briefing",
        "team_approved": False,
        "needs_human_input": False,
        "tasks": [],
        "completed_task_ids": [],
        "failed_task_ids": [],
    }

    res = save_project_state(state)
    assert res is True
    mock_coll.update.assert_called_once()


@patch("neuroforge.workflows.persistence.init_chroma")
@patch("neuroforge.workflows.persistence.get_collection")
def test_load_project_state_returns_none_when_missing(mock_get_coll, mock_init):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}
    mock_get_coll.return_value = mock_coll

    res = load_project_state("missing-p")
    assert res is None


@patch("neuroforge.workflows.persistence.init_chroma")
@patch("neuroforge.workflows.persistence.get_collection")
def test_load_project_state_returns_state_when_found(mock_get_coll, mock_init):
    mock_coll = MagicMock()
    saved_state = {"project_id": "p1", "raw_goal": "build AI"}
    mock_coll.get.return_value = {
        "ids": ["p1"],
        "metadatas": [{"state_json": json.dumps(saved_state)}],
    }
    mock_get_coll.return_value = mock_coll

    res = load_project_state("p1")
    assert res == saved_state


@patch("neuroforge.workflows.persistence.load_project_state")
@patch("neuroforge.workflows.persistence.save_project_state")
def test_update_task_status_updates_correct_task(mock_save, mock_load):
    initial_state = {
        "project_id": "p1",
        "tasks": [
            {"id": "T1", "status": "pending", "started_at": None, "completed_at": None},
            {"id": "T2", "status": "pending", "started_at": None, "completed_at": None},
        ],
    }
    mock_load.return_value = initial_state
    mock_save.return_value = True

    res = update_task_status("p1", "T2", "complete", result="done")
    assert res is True
    assert initial_state["tasks"][0]["status"] == "pending"
    assert initial_state["tasks"][1]["status"] == "complete"
    assert initial_state["tasks"][1]["result"] == "done"
    assert initial_state["tasks"][1]["completed_at"] is not None


@patch("neuroforge.workflows.persistence.init_chroma")
@patch("neuroforge.workflows.persistence.get_collection")
def test_list_projects_returns_metadata(mock_get_coll, mock_init):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {
        "metadatas": [{"project_id": "p1", "current_phase": "briefing"}]
    }
    mock_get_coll.return_value = mock_coll

    res = list_projects()
    assert len(res) == 1
    assert res[0]["project_id"] == "p1"
