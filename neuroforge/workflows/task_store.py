from __future__ import annotations

import json
from datetime import datetime, timezone

from neuroforge.logger import get_logger
from neuroforge.memory.chroma import get_collection, init_chroma

logger = get_logger("task_store")


def save_task_result(
    project_id: str,
    task_id: str,
    result: dict,
    status: str,
) -> bool:
    """Saves a single task result to ChromaDB project_memory.

    Key: {project_id}:task:{task_id} Returns True on success, False on failure.
    """
    try:
        init_chroma()
        collection = get_collection("project_memory")
        doc_id = f"{project_id}:task:{task_id}"
        document = (
            f"Task: {task_id}\n"
            f"Project: {project_id}\n"
            f"Status: {status}\n"
            f"Summary: {result.get('summary', '')}"
        )
        metadata = {
            "project_id": project_id,
            "task_id": task_id,
            "status": status,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "result_json": json.dumps(result),
        }

        existing = collection.get(ids=[doc_id])
        if existing["ids"]:
            collection.update(
                ids=[doc_id], documents=[document], metadatas=[metadata]
            )
        else:
            collection.add(
                ids=[doc_id], documents=[document], metadatas=[metadata]
            )
        return True

    except Exception as e:
        logger.error(
            "save_task_result_failed",
            project_id=project_id,
            task_id=task_id,
            error=str(e),
        )
        return False


def load_task_result(project_id: str, task_id: str) -> dict | None:
    """Loads a single task result from ChromaDB.

    Returns result dict or None if not found.
    """
    try:
        init_chroma()
        collection = get_collection("project_memory")
        doc_id = f"{project_id}:task:{task_id}"
        results = collection.get(ids=[doc_id], include=["metadatas"])
        if not results["ids"]:
            return None
        metadata = results["metadatas"][0]
        result_json = metadata.get("result_json", "{}")
        return json.loads(result_json)
    except Exception as e:
        logger.error(
            "load_task_result_failed",
            project_id=project_id,
            task_id=task_id,
            error=str(e),
        )
        return None


def load_all_task_results(project_id: str) -> dict[str, dict]:
    """Loads all task results for a project.

    Returns dict of {task_id: result_dict}.
    """
    try:
        init_chroma()
        collection = get_collection("project_memory")
        prefix = f"{project_id}:task:"
        all_results = collection.get(include=["ids", "metadatas"])
        task_results = {}
        for doc_id, metadata in zip(
            all_results.get("ids", []), all_results.get("metadatas", [])
        ):
            if doc_id.startswith(prefix):
                task_id = doc_id.replace(prefix, "")
                result_json = metadata.get("result_json", "{}")
                task_results[task_id] = json.loads(result_json)
        return task_results
    except Exception as e:
        logger.error(
            "load_all_task_results_failed", project_id=project_id, error=str(e)
        )
        return {}
