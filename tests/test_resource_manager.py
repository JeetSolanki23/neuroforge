from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from neuroforge.agents.base import AgentInput
from neuroforge.agents.resource_manager import ResourceManager
from neuroforge.config import config


@patch("neuroforge.agents.resource_manager.init_chroma")
@patch("neuroforge.agents.resource_manager.get_collection")
def test_check_availability_no_instances(mock_get_coll, mock_init):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}
    mock_get_coll.return_value = mock_coll

    rm = ResourceManager()
    output = rm.run(AgentInput(task="check:developer"))
    assert output.success is True
    assert output.result["available"] is True
    assert output.result["can_spawn"] is True


@patch("neuroforge.agents.resource_manager.init_chroma")
@patch("neuroforge.agents.resource_manager.get_collection")
def test_check_availability_at_capacity(mock_get_coll, mock_init):
    mock_coll = MagicMock()
    max_inst = config.MAX_INSTANCES_PER_AGENT_TYPE
    instances = [
        {"instance_id": f"dev-{i}", "status": "active"} for i in range(max_inst)
    ]
    mock_coll.get.return_value = {
        "ids": ["resource:developer"],
        "metadatas": [{"instances_json": json.dumps(instances)}],
    }
    mock_get_coll.return_value = mock_coll

    rm = ResourceManager()
    output = rm.run(AgentInput(task="check:developer"))
    assert output.success is True
    assert output.result["available"] is False
    assert output.result["can_spawn"] is False


@patch("neuroforge.agents.resource_manager.init_chroma")
@patch("neuroforge.agents.resource_manager.get_collection")
def test_assign_instance_creates_new(mock_get_coll, mock_init):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}
    mock_get_coll.return_value = mock_coll

    rm = ResourceManager()
    output = rm.run(AgentInput(task="assign:developer:proj-1"))
    assert output.success is True
    assert output.result["reused"] is False
    assert output.result["instance_id"] == "developer-01"


@patch("neuroforge.agents.resource_manager.init_chroma")
@patch("neuroforge.agents.resource_manager.get_collection")
def test_assign_instance_reuses_idle(mock_get_coll, mock_init):
    mock_coll = MagicMock()
    instances = [
        {"instance_id": "developer-01", "status": "idle", "current_project": None}
    ]
    mock_coll.get.return_value = {
        "ids": ["resource:developer"],
        "metadatas": [{"instances_json": json.dumps(instances)}],
    }
    mock_get_coll.return_value = mock_coll

    rm = ResourceManager()
    output = rm.run(AgentInput(task="assign:developer:proj-1"))
    assert output.success is True
    assert output.result["reused"] is True
    assert output.result["instance_id"] == "developer-01"


@patch("neuroforge.agents.resource_manager.init_chroma")
@patch("neuroforge.agents.resource_manager.get_collection")
def test_assign_instance_queued_at_capacity(mock_get_coll, mock_init):
    mock_coll = MagicMock()
    max_inst = config.MAX_INSTANCES_PER_AGENT_TYPE
    instances = [
        {"instance_id": f"dev-{i}", "status": "active", "current_project": "other"}
        for i in range(max_inst)
    ]
    mock_coll.get.return_value = {
        "ids": ["resource:developer"],
        "metadatas": [{"instances_json": json.dumps(instances)}],
    }
    mock_get_coll.return_value = mock_coll

    rm = ResourceManager()
    output = rm._execute(AgentInput(task="assign:developer:proj-1"))
    assert output.success is False
    assert output.result["queued"] is True


@patch("neuroforge.agents.resource_manager.init_chroma")
@patch("neuroforge.agents.resource_manager.get_collection")
def test_release_instance_marks_idle(mock_get_coll, mock_init):
    mock_coll = MagicMock()
    instances = [
        {
            "instance_id": "developer-01",
            "status": "active",
            "current_project": "proj-1",
            "projects_completed": 0,
        }
    ]
    mock_coll.get.return_value = {
        "ids": ["resource:developer"],
        "metadatas": [{"instances_json": json.dumps(instances)}],
    }
    mock_get_coll.return_value = mock_coll

    rm = ResourceManager()
    output = rm.run(AgentInput(task="release:developer:proj-1"))
    assert output.success is True
    assert output.result["released"] is True


@patch("neuroforge.agents.resource_manager.init_chroma")
@patch("neuroforge.agents.resource_manager.get_collection")
def test_release_instance_not_found(mock_get_coll, mock_init):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}
    mock_get_coll.return_value = mock_coll

    rm = ResourceManager()
    output = rm.run(AgentInput(task="release:developer:proj-1"))
    assert output.success is False
    assert "No active instance" in output.error
