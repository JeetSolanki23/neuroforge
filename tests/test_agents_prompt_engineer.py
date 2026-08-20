from __future__ import annotations

import json
import pytest

from neuroforge.agents.base import AgentInput, BaseAgent
from neuroforge.agents.prompt_engineer_agent import PromptEngineerAgent


@pytest.fixture(autouse=True)
def mock_agent_definition(monkeypatch):
    dummy_defn = {
        "id": "prompt-engineer-agent",
        "system_prompt": "You are Prompt Engineer. Respond with valid JSON.",
        "must_not": [],
        "must_always": [],
        "escalate_if": [],
    }
    monkeypatch.setattr(BaseAgent, "get_definition", lambda self: dummy_defn)


def test_prompt_engineer_valid_response(monkeypatch):
    agent = PromptEngineerAgent()
    valid_json = json.dumps({
        "system_prompt": "You are a backend specialist.",
        "must_not": ["Do bad thing"],
        "must_always": ["Do good thing"],
        "escalate_if": ["Error"],
        "reasoning": "Good prompt",
    })
    monkeypatch.setattr(agent, "_call_llm", lambda messages, system, max_tokens=1024: valid_json)

    out = agent.run(AgentInput(task="Draft prompt for backend specialist"))
    assert out.success is True
    assert out.result["system_prompt"] == "You are a backend specialist."


def test_prompt_engineer_invalid_json(monkeypatch):
    agent = PromptEngineerAgent()
    monkeypatch.setattr(agent, "_call_llm", lambda messages, system, max_tokens=1024: "Not JSON")

    out = agent.run(AgentInput(task="Draft prompt"))
    assert out.success is False
    assert "invalid JSON" in (out.error or "")


def test_prompt_engineer_missing_system_prompt_key(monkeypatch):
    agent = PromptEngineerAgent()
    invalid_json = json.dumps({"reasoning": "No prompt"})
    monkeypatch.setattr(agent, "_call_llm", lambda messages, system, max_tokens=1024: invalid_json)

    out = agent.run(AgentInput(task="Draft prompt"))
    assert out.success is False
    assert "missing 'system_prompt' key" in (out.error or "")
