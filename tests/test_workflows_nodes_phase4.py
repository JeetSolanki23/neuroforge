from __future__ import annotations

from unittest.mock import MagicMock, patch

from langgraph.types import Send
from neuroforge.agents.base import AgentOutput
from neuroforge.workflows.nodes import (
    _infer_domain,
    _route_after_task,
    execute_single_task,
    execution_node,
    review_node,
)


@patch("neuroforge.workflows.nodes.save_project_state")
def test_execution_node_returns_task_dict(mock_save):
    state = {
        "project_id": "p1",
        "brief": {
            "functional_requirements": ["Req 1", "Req 2", "Req 3"],
            "parsed_intent": "Intent",
        },
        "team_composition": {
            "specialists": [
                {"role": "backend-specialist"},
                {"role": "frontend-specialist"},
            ]
        },
    }

    result = execution_node(state)
    assert isinstance(result, dict)
    assert len(result["tasks"]) == 3


@patch("neuroforge.workflows.nodes.save_project_state")
def test_execution_node_parallel_assignment(mock_save):
    state = {
        "project_id": "p1",
        "brief": {
            "functional_requirements": ["Req 1", "Req 2", "Req 3"],
        },
        "team_composition": {
            "specialists": [
                {"role": "backend-specialist"},
                {"role": "frontend-specialist"},
            ]
        },
    }

    result = execution_node(state)
    mock_save.assert_called_once()
    saved_state = mock_save.call_args[0][0]
    tasks = saved_state["tasks"]

    assert tasks[0]["assigned_to"] == "backend-specialist"
    assert tasks[1]["assigned_to"] == "frontend-specialist"
    assert tasks[2]["assigned_to"] == "backend-specialist"


@patch("neuroforge.workflows.nodes.save_project_state")
def test_execution_node_dependency_analysis(mock_save):
    state = {
        "project_id": "p1",
        "brief": {
            "functional_requirements": ["Req 1", "Req 2"],
        },
        "team_composition": {
            "specialists": [
                {"role": "backend-specialist"},
            ]
        },
    }

    result = execution_node(state)
    saved_state = mock_save.call_args[0][0]
    tasks = saved_state["tasks"]

    assert tasks[0]["depends_on"] == []
    assert tasks[1]["depends_on"] == ["T1"]


@patch("neuroforge.workflows.task_store.save_task_result")
@patch("neuroforge.agents.specialist_agent.SpecialistAgent.run")
def test_execute_single_task_success(mock_run, mock_save_result):
    mock_run.return_value = AgentOutput(
        success=True,
        result={"summary": "Task complete successfully", "status": "complete"},
    )

    task_input = {
        "project_id": "p1",
        "task": {
            "id": "T1",
            "description": "Do T1",
            "assigned_to": "backend-specialist",
        },
        "brief": {"parsed_intent": "Test"},
        "team_composition": {},
        "attempt": 0,
    }

    res = execute_single_task(task_input)
    assert res["completed_task_ids"] == ["T1"]
    mock_save_result.assert_called_once_with(
        project_id="p1",
        task_id="T1",
        result={"summary": "Task complete successfully", "status": "complete"},
        status="complete",
    )


@patch("neuroforge.workflows.task_store.save_task_result")
@patch("neuroforge.agents.specialist_agent.SpecialistAgent.run")
def test_execute_single_task_failure(mock_run, mock_save_result):
    mock_run.return_value = AgentOutput(
        success=False,
        result=None,
        error="Execution failed",
    )

    task_input = {
        "project_id": "p1",
        "task": {
            "id": "T1",
            "description": "Do T1",
            "assigned_to": "backend-specialist",
        },
        "brief": {},
        "team_composition": {},
        "attempt": 0,
    }

    res = execute_single_task(task_input)
    assert res["failed_task_ids"] == ["T1"]
    mock_save_result.assert_called_once()


def test_route_after_task_all_complete():
    state = {
        "tasks": [{"id": "T1", "depends_on": []}],
        "completed_task_ids": ["T1"],
        "failed_task_ids": [],
    }

    assert _route_after_task(state) == "review"


def test_route_after_task_more_ready():
    state = {
        "project_id": "p1",
        "tasks": [
            {"id": "T1", "depends_on": []},
            {"id": "T2", "depends_on": ["T1"]},
        ],
        "completed_task_ids": ["T1"],
        "failed_task_ids": [],
    }

    res = _route_after_task(state)
    assert isinstance(res, list)
    assert len(res) == 1
    assert isinstance(res[0], Send)


def test_route_after_task_all_blocked():
    state = {
        "project_id": "p1",
        "tasks": [
            {"id": "T1", "depends_on": ["T999"]},
        ],
        "completed_task_ids": [],
        "failed_task_ids": [],
    }

    assert _route_after_task(state) == "review"


@patch("neuroforge.workflows.nodes.save_project_state")
@patch("neuroforge.workflows.nodes._run_memory_distillation")
@patch("neuroforge.workflows.vault_writer.write_project_summary")
@patch("neuroforge.workflows.task_store.load_all_task_results")
def test_review_node_assembles_results(
    mock_load_results, mock_write_summary, mock_distill, mock_save
):
    mock_load_results.return_value = {
        "T1": {"status": "complete", "summary": "Done T1"}
    }
    mock_distill.return_value = []

    state = {
        "project_id": "p1",
        "raw_goal": "Goal",
        "brief": {},
        "completed_task_ids": ["T1"],
        "failed_task_ids": [],
    }

    res = review_node(state)
    assert res["current_phase"] == "complete"
    mock_write_summary.assert_called_once()


def test_infer_domain_keywords():
    assert _infer_domain("backend-django-specialist") == "backend"
    assert _infer_domain("frontend-react-specialist") == "frontend"
    assert _infer_domain("unknown-role") == "general"
