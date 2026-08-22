from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from neuroforge.agents import registry


@pytest.fixture(autouse=True)
def mock_vault_write(monkeypatch):
    monkeypatch.setattr(registry, "_write_vault_entry", lambda defn: None)


def test_is_initialized_returns_false_when_empty(monkeypatch):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}
    monkeypatch.setattr(registry, "get_collection", lambda name: mock_coll)
    monkeypatch.setattr(registry, "init_chroma", lambda: None)

    assert registry.is_initialized() is False


def test_is_initialized_returns_true_when_seeded(monkeypatch):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": ["ceo-orchestrator"]}
    monkeypatch.setattr(registry, "get_collection", lambda name: mock_coll)
    monkeypatch.setattr(registry, "init_chroma", lambda: None)

    assert registry.is_initialized() is True


def test_seed_bootstrap_agents_seeds_all_six(monkeypatch):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}
    monkeypatch.setattr(registry, "get_collection", lambda name: mock_coll)
    monkeypatch.setattr(registry, "init_chroma", lambda: None)

    count = registry.seed_bootstrap_agents()
    assert count == 6
    assert mock_coll.add.call_count == 6


def test_seed_bootstrap_agents_is_idempotent(monkeypatch):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": ["existing_id"]}
    monkeypatch.setattr(registry, "get_collection", lambda name: mock_coll)
    monkeypatch.setattr(registry, "init_chroma", lambda: None)

    count = registry.seed_bootstrap_agents()
    assert count == 6
    assert mock_coll.update.call_count == 6


def test_load_agent_definition_returns_correct_fields(monkeypatch):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {
        "ids": ["hr-agent"],
        "metadatas": [{
            "version": "1.0.0",
            "layer": "bootstrap",
            "name": "HR Agent",
            "role": "Composes teams",
            "domain": "management",
            "system_prompt": "System prompt text",
            "must_not": '["Do not bad thing"]',
            "must_always": '["Do good thing"]',
            "escalate_if": '["Escalate reason"]',
            "projects_used_in": "2",
            "success_rate": "0.95",
        }]
    }
    monkeypatch.setattr(registry, "get_collection", lambda name: mock_coll)
    monkeypatch.setattr(registry, "init_chroma", lambda: None)

    defn = registry.load_agent_definition("hr-agent")
    assert defn["id"] == "hr-agent"
    assert defn["system_prompt"] == "System prompt text"
    assert defn["must_not"] == ["Do not bad thing"]
    assert defn["must_always"] == ["Do good thing"]
    assert defn["escalate_if"] == ["Escalate reason"]
    assert defn["projects_used_in"] == 2
    assert defn["success_rate"] == 0.95


def test_load_agent_definition_raises_for_unknown_id(monkeypatch):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": [], "metadatas": []}
    monkeypatch.setattr(registry, "get_collection", lambda name: mock_coll)
    monkeypatch.setattr(registry, "init_chroma", lambda: None)

    with pytest.raises(RuntimeError, match="Agent 'unknown' not found in registry"):
        registry.load_agent_definition("unknown")


def test_save_agent_definition_returns_true_on_success(monkeypatch):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}
    monkeypatch.setattr(registry, "get_collection", lambda name: mock_coll)
    monkeypatch.setattr(registry, "init_chroma", lambda: None)

    defn = {
        "id": "new-agent",
        "name": "New Agent",
        "role": "New Role",
        "system_prompt": "Prompt",
    }
    assert registry.save_agent_definition(defn) is True
    mock_coll.add.assert_called_once()


def test_list_agent_ids_returns_ids(monkeypatch):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": ["agent1", "agent2"]}
    monkeypatch.setattr(registry, "get_collection", lambda name: mock_coll)
    monkeypatch.setattr(registry, "init_chroma", lambda: None)

    assert registry.list_agent_ids() == ["agent1", "agent2"]
