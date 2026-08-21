from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from neuroforge.agents.base import AgentInput, AgentOutput, BaseAgent


class ConcreteAgent(BaseAgent):
    agent_id = "test-agent"
    name = "Test Agent"
    role = "Testing"
    layer = "bootstrap"

    def __init__(self, fail_attempts: int = 0):
        super().__init__()
        self.fail_attempts = fail_attempts
        self.execute_calls = 0

    def _execute(self, input: AgentInput) -> AgentOutput:
        self.execute_calls += 1
        if self.execute_calls <= self.fail_attempts:
            return AgentOutput(success=False, result=None, error=f"Failure #{self.execute_calls}")
        return AgentOutput(success=True, result="success_result")


@pytest.fixture(autouse=True)
def mock_agent_definition(monkeypatch):
    dummy_defn = {
        "id": "test-agent",
        "system_prompt": "Test system prompt",
        "must_not": ["Do not fail"],
        "must_always": ["Always succeed"],
        "escalate_if": ["Escalate when broken"],
    }
    monkeypatch.setattr(BaseAgent, "get_definition", lambda self: dummy_defn)


def test_agent_succeeds_on_first_attempt():
    agent = ConcreteAgent(fail_attempts=0)
    inp = AgentInput(task="do task")
    out = agent.run(inp)

    assert out.success is True
    assert out.result == "success_result"
    assert agent.execute_calls == 1


def test_agent_retries_on_failure_then_succeeds():
    agent = ConcreteAgent(fail_attempts=2)
    inp = AgentInput(task="do task")
    out = agent.run(inp)

    assert out.success is True
    assert out.result == "success_result"
    assert agent.execute_calls == 3


def test_agent_exhausts_retries_and_escalates():
    agent = ConcreteAgent(fail_attempts=5)
    inp = AgentInput(task="do task")
    out = agent.run(inp)

    assert out.success is False
    assert out.result is None
    assert out.escalate is True
    assert "Max retries exhausted" in (out.escalation_reason or "")
    assert agent.execute_calls == agent.max_retries


def test_agent_output_escalate_false_by_default():
    out = AgentOutput(success=True, result="x")
    assert out.escalate is False
    assert out.error is None
    assert out.escalation_reason is None


def test_agent_input_defaults():
    inp = AgentInput(task="task")
    assert inp.context == {}
    assert inp.project_id is None
