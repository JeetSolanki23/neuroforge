from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from neuroforge.config import config
from neuroforge.logger import get_logger
from neuroforge.memory.chroma import get_collection, init_chroma

logger = get_logger("registry")

BOOTSTRAP_AGENT_IDS = [
    "ceo-orchestrator",
    "hr-agent",
    "prompt-engineer-agent",
    "tool-maker-agent",
    "memory-manager-agent",
    "specialist-base-template",
]


def is_initialized() -> bool:
    """Returns True if bootstrap agents are already seeded in ChromaDB.

    Checks for presence of 'ceo-orchestrator' in agent_definitions.
    """
    try:
        init_chroma()
        collection = get_collection("agent_definitions")
        results = collection.get(ids=["ceo-orchestrator"])
        return len(results["ids"]) > 0
    except Exception:
        return False


def seed_bootstrap_agents() -> int:
    """Seeds all bootstrap agent definitions into ChromaDB and markdown vault.

    Called once on first run. Returns count of agents seeded. Idempotent — safe
    to call multiple times (uses upsert pattern).
    """
    from neuroforge.agents.seed_definitions import BOOTSTRAP_AGENT_DEFINITIONS

    init_chroma()
    collection = get_collection("agent_definitions")
    seeded = 0

    for defn in BOOTSTRAP_AGENT_DEFINITIONS:
        try:
            document = f"{defn['name']}\n\n{defn['role']}\n\n{defn['system_prompt']}"
            metadata = {
                "version": defn["version"],
                "layer": defn["layer"],
                "name": defn["name"],
                "role": defn["role"],
                "domain": defn["domain"],
                "must_not": json.dumps(defn.get("must_not", [])),
                "must_always": json.dumps(defn.get("must_always", [])),
                "escalate_if": json.dumps(defn.get("escalate_if", [])),
                "system_prompt": defn["system_prompt"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "projects_used_in": "0",
                "success_rate": "0.0",
            }

            existing = collection.get(ids=[defn["id"]])
            if existing["ids"]:
                collection.update(
                    ids=[defn["id"]], documents=[document], metadatas=[metadata]
                )
            else:
                collection.add(
                    ids=[defn["id"]], documents=[document], metadatas=[metadata]
                )

            _write_vault_entry(defn)
            seeded += 1
            logger.info("agent_seeded", agent_id=defn["id"])

        except Exception as e:
            logger.error("agent_seed_failed", agent_id=defn["id"], error=str(e))

    return seeded


def load_agent_definition(agent_id: str) -> dict:
    """Loads a single agent definition from ChromaDB by agent_id.

    Returns a dict with all fields including system_prompt, must_not,
    must_always, escalate_if. Raises RuntimeError if agent not found.
    """
    try:
        init_chroma()
        collection = get_collection("agent_definitions")
        results = collection.get(ids=[agent_id], include=["metadatas"])

        if not results["ids"]:
            raise RuntimeError(
                f"Agent '{agent_id}' not found in registry. "
                "Run 'neuroforge init' to seed bootstrap agents."
            )

        metadata = results["metadatas"][0]
        return {
            "id": agent_id,
            "version": metadata.get("version", "1.0.0"),
            "layer": metadata.get("layer", ""),
            "name": metadata.get("name", ""),
            "role": metadata.get("role", ""),
            "domain": metadata.get("domain", ""),
            "system_prompt": metadata.get("system_prompt", ""),
            "must_not": json.loads(metadata.get("must_not", "[]")),
            "must_always": json.loads(metadata.get("must_always", "[]")),
            "escalate_if": json.loads(metadata.get("escalate_if", "[]")),
            "projects_used_in": int(metadata.get("projects_used_in", 0)),
            "success_rate": float(metadata.get("success_rate", 0.0)),
        }

    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to load agent '{agent_id}' from registry: {e}")


def save_agent_definition(defn: dict) -> bool:
    """Saves or updates an agent definition in ChromaDB and vault.

    Used by Prompt Engineer agent when creating or refining agents. Returns
    True on success, False on failure.
    """
    try:
        init_chroma()
        collection = get_collection("agent_definitions")
        document = (
            f"{defn.get('name', '')}\n\n"
            f"{defn.get('role', '')}\n\n"
            f"{defn.get('system_prompt', '')}"
        )
        metadata = {
            "version": defn.get("version", "1.0.0"),
            "layer": defn.get("layer", "dynamic"),
            "name": defn.get("name", ""),
            "role": defn.get("role", ""),
            "domain": defn.get("domain", ""),
            "must_not": json.dumps(defn.get("must_not", [])),
            "must_always": json.dumps(defn.get("must_always", [])),
            "escalate_if": json.dumps(defn.get("escalate_if", [])),
            "system_prompt": defn.get("system_prompt", ""),
            "created_at": defn.get(
                "created_at", datetime.now(timezone.utc).isoformat()
            ),
            "projects_used_in": str(defn.get("projects_used_in", 0)),
            "success_rate": str(defn.get("success_rate", 0.0)),
        }

        existing = collection.get(ids=[defn["id"]])
        if existing["ids"]:
            collection.update(
                ids=[defn["id"]], documents=[document], metadatas=[metadata]
            )
        else:
            collection.add(
                ids=[defn["id"]], documents=[document], metadatas=[metadata]
            )

        _write_vault_entry(defn)
        logger.info(
            "agent_saved", agent_id=defn["id"], version=defn.get("version")
        )
        return True

    except Exception as e:
        logger.error("agent_save_failed", agent_id=defn.get("id"), error=str(e))
        return False


def list_agent_ids(layer: str | None = None) -> list[str]:
    """Returns list of all agent IDs in registry.

    Optionally filter by layer (bootstrap/dynamic/management/orchestration).
    """
    try:
        init_chroma()
        collection = get_collection("agent_definitions")
        where = {"layer": layer} if layer else None
        results = collection.get(where=where, include=["metadatas"])
        return results["ids"]
    except Exception as e:
        logger.error("agent_list_failed", error=str(e))
        return []


def _write_vault_entry(defn: dict) -> None:
    """Writes a human-readable markdown entry to the memory vault.

    Path: memory-vault/agents/{id}/v{version}.md Silent on failure — vault
    write is best-effort.
    """
    try:
        vault_path = Path(config.MEMORY_VAULT_PATH)
        agent_dir = vault_path / "agents" / defn["id"]
        agent_dir.mkdir(parents=True, exist_ok=True)

        version = defn.get("version", "1.0.0")
        filepath = agent_dir / f"v{version}.md"

        content = f"""---
id: {defn["id"]}
version: {version}
layer: {defn.get("layer", "")}
name: {defn.get("name", "")}
domain: {defn.get("domain", "")}
created: {datetime.now(timezone.utc).strftime("%Y-%m-%d")}
tags: [{defn.get("layer", "")}, {defn.get("domain", "")}]
---

# {defn.get("name", defn["id"])}

**Role:** {defn.get("role", "")}
**Layer:** {defn.get("layer", "")}
**Domain:** {defn.get("domain", "")}
**Version:** {version}

## System Prompt

{defn.get("system_prompt", "")}

## Constraints

### Must Not
{chr(10).join(f"- {c}" for c in defn.get("must_not", []))}

### Must Always
{chr(10).join(f"- {c}" for c in defn.get("must_always", []))}

### Escalate If
{chr(10).join(f"- {c}" for c in defn.get("escalate_if", []))}
"""
        filepath.write_text(content, encoding="utf-8")

    except Exception as e:
        logger.warning(
            "vault_write_failed", agent_id=defn.get("id"), error=str(e)
        )
