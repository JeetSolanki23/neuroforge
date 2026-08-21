from __future__ import annotations

from neuroforge.workflows.state import ProjectState, Task, TaskStatus


def test_task_status_constants():
    assert TaskStatus.PENDING == "pending"
    assert TaskStatus.ACTIVE == "active"
    assert TaskStatus.COMPLETE == "complete"
    assert TaskStatus.FAILED == "failed"
    assert TaskStatus.BLOCKED == "blocked"


def test_project_state_has_required_keys():
    state: ProjectState = {
        "project_id": "proj-1",
        "raw_goal": "Build app",
        "brief": None,
        "team_composition": None,
        "team_approved": False,
        "tasks": [],
        "current_phase": "briefing",
        "completed_task_ids": [],
        "failed_task_ids": [],
        "messages": [],
        "error": None,
        "needs_human_input": False,
        "human_input_reason": None,
    }
    assert state["project_id"] == "proj-1"
    assert state["raw_goal"] == "Build app"
    assert state["current_phase"] == "briefing"


def test_task_has_required_keys():
    task: Task = {
        "id": "T1",
        "description": "Do x",
        "assigned_to": "spec-1",
        "depends_on": [],
        "status": TaskStatus.PENDING,
        "result": None,
        "error": None,
        "attempts": 0,
        "started_at": None,
        "completed_at": None,
    }
    assert task["id"] == "T1"
    assert task["status"] == "pending"
