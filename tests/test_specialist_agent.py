from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from neuroforge.agents.base import AgentInput, AgentOutput
from neuroforge.agents.specialist_agent import SpecialistAgent


@pytest.fixture
def dummy_context():
    return {
        "project_name": "Test Project",
        "brief_summary": {
            "scope": "small",
            "functional_requirements": ["Do something"],
        },
        "constraints": ["No downtime"],
    }


@patch("neuroforge.agents.specialist_agent.load_agent_definition")
def test_specialist_agent_valid_response(mock_load_def, dummy_context):
    mock_load_def.return_value = {
        "id": "specialist-base-template",
        "system_prompt": "Role: {role}, Domain: {domain}, Project: {project_name}, Task: {task_description}, Context: {project_context}, Constraints: {constraints}",
    }

    agent = SpecialistAgent(
        role="backend-django-specialist",
        domain="backend",
        project_context=dummy_context,
    )

    valid_json = json.dumps(
        {
            "status": "complete",
            "result": "Created API endpoint",
            "summary": "Finished task successfully",
            "decisions_made": ["Used Django REST framework"],
            "blockers": [],
            "next_steps": ["Write tests"],
        }
    )

    with patch.object(agent, "_call_llm", return_value=valid_json):
        output = agent._execute(AgentInput(task="Build endpoint"))
        assert output.success is True
        assert output.result["status"] == "complete"
        assert output.result["summary"] == "Finished task successfully"


@patch("neuroforge.agents.specialist_agent.load_agent_definition")
def test_specialist_agent_blocked_status(mock_load_def, dummy_context):
    mock_load_def.return_value = {
        "id": "specialist-base-template",
        "system_prompt": "{role} {domain} {project_name} {task_description} {project_context} {constraints}",
    }

    agent = SpecialistAgent(
        role="backend-django-specialist",
        domain="backend",
        project_context=dummy_context,
    )

    blocked_json = json.dumps(
        {
            "status": "blocked",
            "result": None,
            "summary": "Cannot connect to database",
            "decisions_made": [],
            "blockers": ["Database credentials missing"],
            "next_steps": [],
        }
    )

    with patch.object(agent, "_call_llm", return_value=blocked_json):
        output = agent._execute(AgentInput(task="Connect DB"))
        assert output.success is False
        assert output.escalate is True
        assert "Database credentials missing" in output.escalation_reason


@patch("neuroforge.agents.specialist_agent.load_agent_definition")
def test_specialist_agent_failed_status(mock_load_def, dummy_context):
    mock_load_def.return_value = {
        "id": "specialist-base-template",
        "system_prompt": "{role} {domain} {project_name} {task_description} {project_context} {constraints}",
    }

    agent = SpecialistAgent(
        role="backend-django-specialist",
        domain="backend",
        project_context=dummy_context,
    )

    failed_json = json.dumps(
        {
            "status": "failed",
            "result": None,
            "summary": "Execution crashed",
            "decisions_made": [],
            "blockers": [],
            "next_steps": [],
        }
    )

    with patch.object(agent, "_call_llm", return_value=failed_json):
        output = agent._execute(AgentInput(task="Run script"))
        assert output.success is False
        assert "Specialist reported failure" in output.error


@patch("neuroforge.agents.specialist_agent.load_agent_definition")
def test_specialist_agent_invalid_json(mock_load_def, dummy_context):
    mock_load_def.return_value = {
        "id": "specialist-base-template",
        "system_prompt": "{role} {domain} {project_name} {task_description} {project_context} {constraints}",
    }

    agent = SpecialistAgent(
        role="backend-django-specialist",
        domain="backend",
        project_context=dummy_context,
    )

    with patch.object(agent, "_call_llm", return_value="Not JSON"):
        output = agent._execute(AgentInput(task="Task"))
        assert output.success is False
        assert "invalid JSON" in output.error


@patch("neuroforge.agents.specialist_agent.load_agent_definition")
def test_specialist_agent_missing_keys(mock_load_def, dummy_context):
    mock_load_def.return_value = {
        "id": "specialist-base-template",
        "system_prompt": "{role} {domain} {project_name} {task_description} {project_context} {constraints}",
    }

    agent = SpecialistAgent(
        role="backend-django-specialist",
        domain="backend",
        project_context=dummy_context,
    )

    incomplete_json = json.dumps(
        {
            "status": "complete",
            "result": "Done",
            # missing summary
        }
    )

    with patch.object(agent, "_call_llm", return_value=incomplete_json):
        output = agent._execute(AgentInput(task="Task"))
        assert output.success is False
        assert "missing keys" in output.error


@patch("neuroforge.agents.specialist_agent.load_agent_definition")
def test_specialist_agent_context_injection(mock_load_def, dummy_context):
    mock_load_def.return_value = {
        "id": "specialist-base-template",
        "system_prompt": "Role: {role} | Domain: {domain} | Project: {project_name} | Task: {task_description} | Context: {project_context} | Constraints: {constraints}",
    }

    agent = SpecialistAgent(
        role="backend-django-specialist",
        domain="backend",
        project_context=dummy_context,
    )

    prompt = agent._build_system_prompt("Build API")
    assert "backend-django-specialist" in prompt
    assert "backend" in prompt
    assert "Test Project" in prompt
    assert "Build API" in prompt
    assert "No downtime" in prompt


def test_specialist_agent_domain_inference():
    agent = SpecialistAgent(
        role="backend-django-specialist",
        domain="backend",
        project_context={},
    )
    assert agent.domain == "backend"
