from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from neuroforge.config import config
from neuroforge.logger import get_logger
from neuroforge.memory.chroma import get_collection, init_chroma

logger = get_logger("persistence")


def _get_vault_state_path(project_id: str) -> Path:
    """Returns Path: config.MEMORY_VAULT_PATH / "projects" / project_id / "state.json"
    Creates parent directories if they don't exist.
    """
    vault_path = Path(config.MEMORY_VAULT_PATH)
    project_dir = vault_path / "projects" / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir / "state.json"


def save_project_state(state: dict) -> bool:
    """Saves full ProjectState to vault file and lightweight metadata to ChromaDB.

    Uses project_id as the document ID. Upserts — safe to call on every state
    change. Returns True on success, False on failure.
    """
    try:
        project_id = state["project_id"]
        state_path = _get_vault_state_path(project_id)
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

        init_chroma()
        collection = get_collection("project_memory")

        document = f"Project: {project_id}\nGoal: {state.get('raw_goal', '')}"
        metadata = {
            "project_id": project_id,
            "current_phase": state.get("current_phase", ""),
            "team_approved": str(state.get("team_approved", False)),
            "needs_human_input": str(state.get("needs_human_input", False)),
            "task_count": str(len(state.get("tasks", []))),
            "completed_count": str(len(state.get("completed_task_ids", []))),
            "failed_count": str(len(state.get("failed_task_ids", []))),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "vault_path": str(state_path),
        }

        existing = collection.get(ids=[project_id])
        if existing["ids"]:
            collection.update(
                ids=[project_id], documents=[document], metadatas=[metadata]
            )
        else:
            collection.add(
                ids=[project_id], documents=[document], metadatas=[metadata]
            )
        return True

    except Exception as e:
        logger.error(
            "save_project_state_failed",
            project_id=state.get("project_id"),
            error=str(e),
        )
        return False


def load_project_state(project_id: str) -> dict | None:
    """Loads ProjectState from vault file referenced in ChromaDB metadata.

    Returns the state dict or None if not found or vault file missing.
    """
    try:
        init_chroma()
        collection = get_collection("project_memory")
        results = collection.get(ids=[project_id], include=["metadatas"])
        if not results["ids"]:
            return None
        metadata = results["metadatas"][0]
        vault_path_str = metadata.get("vault_path")
        if not vault_path_str:
            # Fallback for legacy state records if any
            state_json = metadata.get("state_json")
            if state_json:
                return json.loads(state_json)
            return None

        vault_path = Path(vault_path_str)
        if not vault_path.exists():
            return None

        content = vault_path.read_text(encoding="utf-8")
        return json.loads(content)
    except Exception as e:
        logger.error(
            "load_project_state_failed", project_id=project_id, error=str(e)
        )
        return None


def update_task_status(
    project_id: str,
    task_id: str,
    status: str,
    result: str | None = None,
    error: str | None = None,
) -> bool:
    """Loads project state, updates a single task's status, saves back.

    Returns True on success, False on failure.
    """
    state = load_project_state(project_id)
    if state is None:
        logger.error("update_task_status_no_state", project_id=project_id)
        return False

    now = datetime.now(timezone.utc).isoformat()
    for task in state.get("tasks", []):
        if task["id"] == task_id:
            task["status"] = status
            if result is not None:
                task["result"] = result
            if error is not None:
                task["error"] = error
            if status == "active" and task.get("started_at") is None:
                task["started_at"] = now
            if status in ("complete", "failed"):
                task["completed_at"] = now
            break

    return save_project_state(state)


def list_projects(phase: str | None = None) -> list[dict]:
    """Returns list of all projects in project_memory.

    Optionally filter by current_phase. Returns list of metadata dicts (not full
    state).
    """
    try:
        init_chroma()
        collection = get_collection("project_memory")
        where = {"current_phase": phase} if phase else None
        results = collection.get(where=where, include=["metadatas"])
        return results.get("metadatas", [])
    except Exception as e:
        logger.error("list_projects_failed", error=str(e))
        return []
