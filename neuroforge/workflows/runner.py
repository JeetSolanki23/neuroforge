from __future__ import annotations

import uuid
from datetime import datetime, timezone

from neuroforge.logger import get_logger
from neuroforge.workflows.graph import build_project_graph
from neuroforge.workflows.persistence import save_project_state
from neuroforge.workflows.state import ProjectState

logger = get_logger("runner")


def run_project(goal: str) -> dict:
    """Runs a full project from goal to completion.

    Builds a fresh graph instance, initialises state, invokes graph. Returns the
    final ProjectState dict.
    """
    project_id = f"project-{uuid.uuid4().hex[:8]}"
    logger.info("project_start", project_id=project_id, goal=goal[:80])

    initial_state: ProjectState = {
        "project_id": project_id,
        "raw_goal": goal,
        "brief": None,
        "team_composition": None,
        "team_approved": False,
        "tasks": [],
        "current_phase": "briefing",
        "completed_task_ids": [],
        "failed_task_ids": [],
        "messages": [
            f"[{datetime.now(timezone.utc).isoformat()}] Project started: {goal}"
        ],
        "error": None,
        "needs_human_input": False,
        "human_input_reason": None,
    }

    # Persist initial state immediately
    save_project_state(initial_state)

    graph = build_project_graph()

    try:
        final_state = graph.invoke(initial_state)
        logger.info(
            "project_complete",
            project_id=project_id,
            phase=final_state.get("current_phase"),
        )
        return final_state

    except Exception as e:
        logger.error("project_failed", project_id=project_id, error=str(e))
        error_state = {
            **initial_state,
            "current_phase": "failed",
            "error": str(e),
        }
        save_project_state(error_state)
        return error_state
