from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from neuroforge.logger import get_logger
from neuroforge.workflows.persistence import save_project_state, update_task_status
from neuroforge.workflows.state import ProjectState, Task, TaskStatus

logger = get_logger("nodes")


def briefing_node(state: ProjectState) -> dict:
    """Node 1: CEO produces Project Brief from raw goal.

    Uses CEOAgent (imported lazily to avoid circular imports). Saves state after
    brief is produced. Returns: updates to brief, current_phase, messages
    """
    from neuroforge.agents.base import AgentInput
    from neuroforge.agents.ceo_agent import CEOAgent

    logger.info("briefing_node_start", project_id=state["project_id"])
    agent = CEOAgent()

    # Query memory for similar projects to include in context
    similar = _query_similar_projects(state["raw_goal"])

    task_input = json.dumps({"goal": state["raw_goal"], "similar_projects": similar})

    output = agent.run(AgentInput(task=task_input, project_id=state["project_id"]))

    if not output.success:
        updates = {
            "current_phase": "failed",
            "error": f"Briefing failed: {output.error}",
            "messages": [f"[briefing] FAILED: {output.error}"],
            "needs_human_input": output.escalate,
            "human_input_reason": output.escalation_reason,
        }
        save_project_state({**state, **updates})
        return updates

    brief = output.result
    updates = {
        "brief": brief,
        "current_phase": "team_formation",
        "messages": [f"[briefing] Brief produced. Scope: {brief.get('scope')}"],
    }
    save_project_state({**state, **updates})
    return updates


def team_formation_node(state: ProjectState) -> dict:
    """Node 2: HR Agent composes team from brief.

    Saves state after team is proposed. Returns: updates to team_composition,
    team_approved, messages
    """
    from neuroforge.agents.base import AgentInput
    from neuroforge.agents.hr_agent import HRAgent
    from neuroforge.agents.registry import list_agent_ids

    logger.info("team_formation_node_start", project_id=state["project_id"])
    agent = HRAgent()

    available_agents = list_agent_ids()
    brief_str = json.dumps(state["brief"])

    output = agent.run(
        AgentInput(
            task=brief_str,
            context={"available_agent_types": available_agents},
            project_id=state["project_id"],
        )
    )

    if not output.success:
        updates = {
            "current_phase": "failed",
            "error": f"Team formation failed: {output.error}",
            "messages": [f"[team_formation] FAILED: {output.error}"],
            "needs_human_input": output.escalate,
            "human_input_reason": output.escalation_reason,
        }
        save_project_state({**state, **updates})
        return updates

    team = output.result
    new_types = team.get("new_agent_types_needed", [])

    updates = {
        "team_composition": team,
        "team_approved": len(new_types) == 0,
        "current_phase": "execution" if len(new_types) == 0 else "failed",
        "messages": [
            f"[team_formation] Team composed. "
            f"Leads: {len(team.get('team_leads', []))}, "
            f"Specialists: {len(team.get('specialists', []))}."
        ],
        "needs_human_input": len(new_types) > 0,
        "human_input_reason": (
            f"New agent types needed: {new_types}" if new_types else None
        ),
    }
    save_project_state({**state, **updates})
    return updates


def execution_node(state: ProjectState) -> dict:
    """Node 3: Project Manager builds task DAG and executes tasks.

    For Phase 3 this builds the DAG and marks tasks as pending. Actual
    specialist agent execution comes in Phase 4. Saves state after DAG is built.
    Returns: updates to tasks, current_phase, messages
    """
    logger.info("execution_node_start", project_id=state["project_id"])

    brief = state.get("brief", {}) or {}
    team = state.get("team_composition", {}) or {}
    specialists = team.get("specialists", [])
    requirements = brief.get("functional_requirements", [])

    # Build task DAG from requirements and team
    # Phase 3: one task per requirement, assigned to first available specialist
    # Phase 4: proper dependency analysis and parallel assignment
    tasks: list[Task] = []
    for i, req in enumerate(requirements):
        task_id = f"T{i + 1}"
        assigned = (
            specialists[i % len(specialists)]["role"]
            if specialists
            else "unassigned"
        )
        task: Task = {
            "id": task_id,
            "description": req,
            "assigned_to": assigned,
            "depends_on": [f"T{i}"] if i > 0 else [],
            "status": TaskStatus.PENDING,
            "result": None,
            "error": None,
            "attempts": 0,
            "started_at": None,
            "completed_at": None,
        }
        tasks.append(task)
        update_task_status(state["project_id"], task_id, TaskStatus.PENDING)

    updates = {
        "tasks": tasks,
        "current_phase": "review",
        "messages": [
            f"[execution] DAG built: {len(tasks)} tasks. "
            f"Specialist execution pending (Phase 4)."
        ],
    }
    save_project_state({**state, **updates})
    return updates


def review_node(state: ProjectState) -> dict:
    """Node 4: Reviews project completion and triggers Memory Manager.

    In Phase 3, since specialist agents don't run yet, marks project complete
    with DAG-built status. Saves final state. Returns: updates to
    current_phase, messages
    """
    logger.info("review_node_start", project_id=state["project_id"])

    task_count = len(state.get("tasks", []))
    updates = {
        "current_phase": "complete",
        "messages": [
            f"[review] Project DAG complete. "
            f"{task_count} tasks staged for execution (Phase 4). "
            f"Memory distillation pending."
        ],
    }
    save_project_state({**state, **updates})
    return updates


def _query_similar_projects(goal: str) -> list[str]:
    """Helper: semantic search in project_briefs for similar past goals.

    Returns list of project_id strings. Silent on failure.
    """
    try:
        from neuroforge.memory.chroma import get_collection, init_chroma

        init_chroma()
        collection = get_collection("project_briefs")
        results = collection.query(query_texts=[goal], n_results=3)
        return results.get("ids", [[]])[0]
    except Exception:
        return []


def _route_after_briefing(state: ProjectState) -> str:
    """Conditional edge: where to go after briefing node."""
    if state.get("current_phase") == "failed":
        return "end"
    return "team_formation"


def _route_after_team_formation(state: ProjectState) -> str:
    """Conditional edge: where to go after team formation node."""
    if state.get("current_phase") == "failed":
        return "end"
    if not state.get("team_approved"):
        return "end"
    return "execution"


def _route_after_execution(state: ProjectState) -> str:
    """Conditional edge: where to go after execution node."""
    if state.get("current_phase") == "failed":
        return "end"
    return "review"
