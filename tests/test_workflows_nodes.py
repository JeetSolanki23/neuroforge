from __future__ import annotations

from unittest.mock import MagicMock, patch

from neuroforge.agents.base import AgentOutput
from neuroforge.workflows.nodes import (
    _route_after_briefing,
    _route_after_execution,
    _route_after_team_formation,
    briefing_node,
    execution_node,
    review_node,
    team_formation_node,
)
from neuroforge.workflows.state import TaskStatus


@patch("neuroforge.workflows.nodes.save_project_state")
@patch("neuroforge.workflows.nodes._query_similar_projects")
@patch("neuroforge.agents.ceo_agent.CEOAgent.run")
def test_briefing_node_success(mock_ceo_run, mock_similar, mock_save):
    mock_similar.return_value = []
    brief = {
        "raw_goal": "Goal",
        "parsed_intent": "Intent",
        "scope": "small",
        "functional_requirements": ["req1"],
        "acceptance_criteria": ["crit1"],
    }
    mock_ceo_run.return_value = AgentOutput(success=True, result=brief)

    state = {
        "project_id": "p1",
        "raw_goal": "Goal",
        "brief": None,
        "current_phase": "briefing",
        "messages": [],
    }

    updates = briefing_node(state)
    assert updates["brief"] == brief
    assert updates["current_phase"] == "team_formation"
    assert len(updates["messages"]) == 1


@patch("neuroforge.workflows.nodes.save_project_state")
@patch("neuroforge.workflows.nodes._query_similar_projects")
@patch("neuroforge.agents.ceo_agent.CEOAgent.run")
def test_briefing_node_failure(mock_ceo_run, mock_similar, mock_save):
    mock_similar.return_value = []
    mock_ceo_run.return_value = AgentOutput(
        success=False, result=None, error="Failed LLM", escalate=True, escalation_reason="Error"
    )

    state = {
        "project_id": "p1",
        "raw_goal": "Goal",
        "brief": None,
        "current_phase": "briefing",
        "messages": [],
    }

    updates = briefing_node(state)
    assert updates["current_phase"] == "failed"
    assert "Briefing failed: Failed LLM" in updates["error"]


@patch("neuroforge.workflows.nodes.save_project_state")
@patch("neuroforge.agents.registry.list_agent_ids")
@patch("neuroforge.agents.hr_agent.HRAgent.run")
def test_team_formation_node_success(mock_hr_run, mock_list_ids, mock_save):
    mock_list_ids.return_value = ["developer-agent"]
    team = {
        "team_leads": [],
        "specialists": [{"role": "developer-agent"}],
        "new_agent_types_needed": [],
    }
    mock_hr_run.return_value = AgentOutput(success=True, result=team)

    state = {
        "project_id": "p1",
        "brief": {"scope": "small"},
        "current_phase": "team_formation",
        "messages": [],
    }

    updates = team_formation_node(state)
    assert updates["team_approved"] is True
    assert updates["current_phase"] == "execution"
    assert updates["team_composition"] == team


@patch("neuroforge.workflows.nodes.save_project_state")
@patch("neuroforge.agents.registry.list_agent_ids")
@patch("neuroforge.agents.hr_agent.HRAgent.run")
def test_team_formation_node_needs_new_agents(mock_hr_run, mock_list_ids, mock_save):
    mock_list_ids.return_value = []
    team = {
        "team_leads": [],
        "specialists": [],
        "new_agent_types_needed": ["custom-agent"],
    }
    mock_hr_run.return_value = AgentOutput(success=True, result=team)

    state = {
        "project_id": "p1",
        "brief": {"scope": "small"},
        "current_phase": "team_formation",
        "messages": [],
    }

    updates = team_formation_node(state)
    assert updates["team_approved"] is False
    assert updates["current_phase"] == "failed"
    assert updates["needs_human_input"] is True


@patch("neuroforge.workflows.nodes.save_project_state")
@patch("neuroforge.workflows.nodes.update_task_status")
def test_execution_node_builds_dag(mock_update_task, mock_save):
    state = {
        "project_id": "p1",
        "brief": {
            "functional_requirements": ["req1", "req2", "req3"],
        },
        "team_composition": {
            "specialists": [{"role": "dev-1"}],
        },
        "current_phase": "execution",
        "tasks": [],
        "messages": [],
    }

    updates = execution_node(state)
    assert len(updates["tasks"]) == 3
    assert updates["current_phase"] == "review"
    assert updates["tasks"][0]["status"] == TaskStatus.PENDING
    assert updates["tasks"][1]["depends_on"] == ["T1"]


@patch("neuroforge.workflows.nodes.save_project_state")
def test_review_node_marks_complete(mock_save):
    state = {
        "project_id": "p1",
        "tasks": [{"id": "T1"}],
        "current_phase": "review",
        "messages": [],
    }

    updates = review_node(state)
    assert updates["current_phase"] == "complete"


def test_route_after_briefing_success():
    state = {"current_phase": "team_formation"}
    assert _route_after_briefing(state) == "team_formation"


def test_route_after_briefing_failure():
    state = {"current_phase": "failed"}
    assert _route_after_briefing(state) == "end"


def test_route_after_team_formation_approved():
    state = {"current_phase": "execution", "team_approved": True}
    assert _route_after_team_formation(state) == "execution"


def test_route_after_team_formation_not_approved():
    state = {"current_phase": "failed", "team_approved": False}
    assert _route_after_team_formation(state) == "end"
