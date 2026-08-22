from __future__ import annotations

import json
from unittest.mock import patch

from neuroforge.agents.base import AgentInput
from neuroforge.agents.ceo_agent import CEOAgent


@patch.object(CEOAgent, "get_definition")
@patch("neuroforge.agents.base.call_llm")
def test_ceo_valid_response(mock_call_llm, mock_get_def):
    mock_get_def.return_value = {"system_prompt": "You are CEO."}
    valid_data = {
        "raw_goal": "Build an app",
        "parsed_intent": "Build web app",
        "scope": "small",
        "functional_requirements": ["Requirement 1"],
        "acceptance_criteria": ["Criteria 1"],
    }
    mock_call_llm.return_value = json.dumps(valid_data)

    ceo = CEOAgent()
    output = ceo.run(AgentInput(task="Build app"))
    assert output.success is True
    assert output.result["parsed_intent"] == "Build web app"


@patch.object(CEOAgent, "get_definition")
@patch("neuroforge.agents.base.call_llm")
def test_ceo_invalid_json(mock_call_llm, mock_get_def):
    mock_get_def.return_value = {"system_prompt": "You are CEO."}
    mock_call_llm.return_value = "not valid json"

    ceo = CEOAgent()
    output = ceo.run(AgentInput(task="Build app"))
    assert output.success is False
    assert "invalid JSON" in output.error


@patch.object(CEOAgent, "get_definition")
@patch("neuroforge.agents.base.call_llm")
def test_ceo_missing_keys(mock_call_llm, mock_get_def):
    mock_get_def.return_value = {"system_prompt": "You are CEO."}
    invalid_data = {
        "raw_goal": "Build an app",
        "parsed_intent": "Build web app",
        "scope": "small",
        # missing functional_requirements & acceptance_criteria
    }
    mock_call_llm.return_value = json.dumps(invalid_data)

    ceo = CEOAgent()
    output = ceo.run(AgentInput(task="Build app"))
    assert output.success is False
    assert "missing keys" in output.error


@patch.object(CEOAgent, "get_definition")
@patch("neuroforge.agents.base.call_llm")
def test_ceo_invalid_scope(mock_call_llm, mock_get_def):
    mock_get_def.return_value = {"system_prompt": "You are CEO."}
    invalid_data = {
        "raw_goal": "Build an app",
        "parsed_intent": "Build web app",
        "scope": "huge",
        "functional_requirements": ["req"],
        "acceptance_criteria": ["crit"],
    }
    mock_call_llm.return_value = json.dumps(invalid_data)

    ceo = CEOAgent()
    output = ceo.run(AgentInput(task="Build app"))
    assert output.success is False
    assert "invalid scope" in output.error
