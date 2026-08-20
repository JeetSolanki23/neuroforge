from __future__ import annotations

import json
import pytest

from neuroforge.agents.base import AgentInput, BaseAgent
from neuroforge.agents.tool_maker_agent import ToolMakerAgent


@pytest.fixture(autouse=True)
def mock_agent_definition(monkeypatch):
    dummy_defn = {
        "id": "tool-maker-agent",
        "system_prompt": "You are Tool Maker. Respond with valid JSON.",
        "must_not": [],
        "must_always": [],
        "escalate_if": [],
    }
    monkeypatch.setattr(BaseAgent, "get_definition", lambda self: dummy_defn)


def test_tool_maker_valid_response(monkeypatch):
    agent = ToolMakerAgent()
    valid_json = json.dumps({
        "tool_id": "file_reader",
        "name": "File Reader",
        "category": "file_tools",
        "description": "Reads files",
        "function_name": "read_file",
        "parameters": {},
        "returns": {"type": "string", "description": "content"},
        "dependencies": [],
        "implementation_notes": "notes",
    })
    monkeypatch.setattr(agent, "_call_llm", lambda messages, system, max_tokens=1024: valid_json)

    out = agent.run(AgentInput(task="Design file reader tool"))
    assert out.success is True
    assert out.result["tool_id"] == "file_reader"
    assert out.result["category"] == "file_tools"


def test_tool_maker_invalid_json(monkeypatch):
    agent = ToolMakerAgent()
    monkeypatch.setattr(agent, "_call_llm", lambda messages, system, max_tokens=1024: "Not JSON")

    out = agent.run(AgentInput(task="Design tool"))
    assert out.success is False
    assert "invalid JSON" in (out.error or "")


def test_tool_maker_invalid_category(monkeypatch):
    agent = ToolMakerAgent()
    invalid_json = json.dumps({
        "tool_id": "tool_1",
        "name": "Tool",
        "category": "invalid_cat",
        "description": "desc",
        "function_name": "func",
    })
    monkeypatch.setattr(agent, "_call_llm", lambda messages, system, max_tokens=1024: invalid_json)

    out = agent.run(AgentInput(task="Design tool"))
    assert out.success is False
    assert "invalid category" in (out.error or "")


def test_tool_maker_missing_required_keys(monkeypatch):
    agent = ToolMakerAgent()
    invalid_json = json.dumps({
        "tool_id": "tool_1",
        "name": "Tool",
    })
    monkeypatch.setattr(agent, "_call_llm", lambda messages, system, max_tokens=1024: invalid_json)

    out = agent.run(AgentInput(task="Design tool"))
    assert out.success is False
    assert "missing keys" in (out.error or "")
