from __future__ import annotations

import json
import pytest
from unittest.mock import MagicMock

from neuroforge.agents.base import AgentInput, BaseAgent
from neuroforge.agents.memory_manager_agent import MemoryManagerAgent
from neuroforge.agents import memory_manager_agent


@pytest.fixture(autouse=True)
def mock_agent_definition(monkeypatch):
    dummy_defn = {
        "id": "memory-manager-agent",
        "system_prompt": "You are Memory Manager. Respond with valid JSON.",
        "must_not": [],
        "must_always": [],
        "escalate_if": [],
    }
    monkeypatch.setattr(BaseAgent, "get_definition", lambda self: dummy_defn)


def test_memory_manager_stores_entries(monkeypatch):
    agent = MemoryManagerAgent()
    mock_coll = MagicMock()
    monkeypatch.setattr(memory_manager_agent, "get_collection", lambda name: mock_coll)

    valid_json = json.dumps({
        "learned_entries": [
            {
                "title": "Learning 1",
                "content": "Content 1",
                "domain": ["backend"],
                "applies_to_agents": ["backend-specialist"],
                "confidence": "high",
                "tags": ["django"],
                "surface_to_human": False,
            }
        ],
        "summary": "Project summary text",
    })
    monkeypatch.setattr(agent, "_call_llm", lambda messages, system, max_tokens=1024: valid_json)

    out = agent.run(AgentInput(task="[]", project_id="proj-101"))
    assert out.success is True
    assert out.result["stored_count"] == 1
    assert out.result["summary"] == "Project summary text"
    mock_coll.add.assert_called_once()


def test_memory_manager_flags_surface_to_human(monkeypatch):
    agent = MemoryManagerAgent()
    mock_coll = MagicMock()
    monkeypatch.setattr(memory_manager_agent, "get_collection", lambda name: mock_coll)

    valid_json = json.dumps({
        "learned_entries": [
            {
                "title": "Critical Learning",
                "content": "Content",
                "domain": ["security"],
                "applies_to_agents": ["all"],
                "confidence": "confirmed",
                "tags": ["auth"],
                "surface_to_human": True,
                "surface_reason": "Security vulnerability pattern",
            }
        ],
        "summary": "Summary",
    })
    monkeypatch.setattr(agent, "_call_llm", lambda messages, system, max_tokens=1024: valid_json)

    out = agent.run(AgentInput(task="[]", project_id="proj-102"))
    assert out.success is True
    assert len(out.result["surface_to_human"]) == 1
    assert out.result["surface_to_human"][0]["reason"] == "Security vulnerability pattern"


def test_memory_manager_requires_project_id(monkeypatch):
    agent = MemoryManagerAgent()
    out = agent.run(AgentInput(task="[]"))
    assert out.success is False
    assert "requires project_id" in (out.error or "")


def test_memory_manager_invalid_json(monkeypatch):
    agent = MemoryManagerAgent()
    monkeypatch.setattr(agent, "_call_llm", lambda messages, system, max_tokens=1024: "Not JSON")

    out = agent.run(AgentInput(task="[]", project_id="proj-103"))
    assert out.success is False
    assert "invalid JSON" in (out.error or "")


def test_memory_manager_partial_failure(monkeypatch):
    agent = MemoryManagerAgent()
    mock_coll = MagicMock()

    # Fail on first call, succeed on second
    mock_coll.add.side_effect = [Exception("Add failed"), None]
    monkeypatch.setattr(memory_manager_agent, "get_collection", lambda name: mock_coll)

    valid_json = json.dumps({
        "learned_entries": [
            {"title": "Entry 1", "content": "C1", "domain": ["d1"], "confidence": "low"},
            {"title": "Entry 2", "content": "C2", "domain": ["d2"], "confidence": "medium"},
        ],
        "summary": "Summary",
    })
    monkeypatch.setattr(agent, "_call_llm", lambda messages, system, max_tokens=1024: valid_json)

    out = agent.run(AgentInput(task="[]", project_id="proj-104"))
    assert out.success is True
    assert out.result["stored_count"] == 1
