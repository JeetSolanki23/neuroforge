from __future__ import annotations

import json
import pytest
from unittest.mock import MagicMock

from neuroforge.agents.base import AgentInput, BaseAgent
from neuroforge.agents.hr_agent import HRAgent


@pytest.fixture(autouse=True)
def mock_agent_definition(monkeypatch):
    dummy_defn = {
        "id": "hr-agent",
        "system_prompt": "You are HR Agent. Respond with valid JSON.",
        "must_not": [],
        "must_always": [],
        "escalate_if": [],
    }
    monkeypatch.setattr(BaseAgent, "get_definition", lambda self: dummy_defn)


def test_hr_agent_valid_response(monkeypatch):
    agent = HRAgent()
    valid_json = json.dumps({
        "scope_assessment": "small",
        "requires_team_leads": False,
        "team_leads": [],
        "specialists": [{"role": "backend", "domain": "backend", "reports_to": "project_manager"}],
        "new_agent_types_needed": [],
        "reasoning": "Small project needing backend",
    })
    monkeypatch.setattr(agent, "_call_llm", lambda messages, system, max_tokens=1024: valid_json)

    out = agent.run(AgentInput(task="Brief task"))
    assert out.success is True
    assert out.result["scope_assessment"] == "small"
    assert out.result["requires_team_leads"] is False


def test_hr_agent_invalid_json(monkeypatch):
    agent = HRAgent()
    monkeypatch.setattr(agent, "_call_llm", lambda messages, system, max_tokens=1024: "Not JSON")

    out = agent.run(AgentInput(task="Brief task"))
    assert out.success is False
    assert "invalid JSON" in (out.error or "")


def test_hr_agent_missing_keys(monkeypatch):
    agent = HRAgent()
    invalid_json = json.dumps({
        "scope_assessment": "small",
        "reasoning": "Missing keys",
    })
    monkeypatch.setattr(agent, "_call_llm", lambda messages, system, max_tokens=1024: invalid_json)

    out = agent.run(AgentInput(task="Brief task"))
    assert out.success is False
    assert "missing keys" in (out.error or "")


def test_hr_agent_includes_available_agents_in_context(monkeypatch):
    agent = HRAgent()
    captured_messages = []

    def mock_call(messages, system, max_tokens=1024):
        captured_messages.extend(messages)
        return json.dumps({
            "scope_assessment": "small",
            "requires_team_leads": False,
            "specialists": [],
            "reasoning": "ok",
        })

    monkeypatch.setattr(agent, "_call_llm", mock_call)

    agent.run(AgentInput(
        task="Brief task",
        context={"available_agent_types": ["backend-specialist", "frontend-specialist"]}
    ))

    assert len(captured_messages) == 1
    assert "Available agent types in registry:" in captured_messages[0]["content"]
    assert "backend-specialist" in captured_messages[0]["content"]
