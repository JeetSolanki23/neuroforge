from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from langgraph.types import Send

from neuroforge.logger import get_logger
from neuroforge.workflows.persistence import save_project_state, update_task_status
from neuroforge.workflows.state import ProjectState, Task, TaskStatus

logger = get_logger("nodes")


def execute_single_task(task_input: dict) -> dict:
    """Executes a single task using a SpecialistAgent.

    Called in parallel by LangGraph Send for each ready task.

    task_input dict contains:
      project_id: str
      task: Task dict
      brief: dict
      team_composition: dict
      attempt: int (default 0)

    Returns dict with state updates:
      completed_task_ids or failed_task_ids (list to append)
      messages (list to append)
    """
    from neuroforge.agents.base import AgentInput
    from neuroforge.agents.specialist_agent import SpecialistAgent
    from neuroforge.workflows.task_store import save_task_result

    project_id = task_input["project_id"]
    task = task_input["task"]
    brief = task_input.get("brief", {})
    team = task_input.get("team_composition", {})
    attempt = task_input.get("attempt", 0)

    task_id = task["id"]
    assigned_to = task["assigned_to"]

    # Build project context for the specialist
    project_context = {
        "project_name": brief.get("parsed_intent", "Unknown project"),
        "brief_summary": {
            "scope": brief.get("scope"),
            "functional_requirements": brief.get(
                "functional_requirements", []
            ),
            "acceptance_criteria": brief.get("acceptance_criteria", []),
        },
        "constraints": brief.get("constraints", []),
    }

    # Determine domain from assigned_to role
    domain = _infer_domain(assigned_to)

    agent = SpecialistAgent(
        role=assigned_to, domain=domain, project_context=project_context
    )

    output = agent.run(
        AgentInput(
            task=task["description"],
            context={"task_id": task_id, "attempt": attempt},
            project_id=project_id,
        )
    )

    if output.success:
        save_task_result(
            project_id=project_id,
            task_id=task_id,
            result=output.result,
            status="complete",
        )
        return {
            "completed_task_ids": [task_id],
            "messages": [
                f"[task:{task_id}] Complete — {assigned_to}: "
                f"{output.result.get('summary', '')[:100]}"
            ],
        }
    else:
        save_task_result(
            project_id=project_id,
            task_id=task_id,
            result={"error": output.error, "status": "failed"},
            status="failed",
        )
        return {
            "failed_task_ids": [task_id],
            "messages": [
                f"[task:{task_id}] FAILED — {assigned_to}: {output.error}"
            ],
        }


def _infer_domain(role: str) -> str:
    """Infers domain from role string.

    e.g. "backend-django-specialist" → "backend" "frontend-react-specialist" →
    "frontend" "qa-pytest-specialist" → "qa" Falls back to "general" if no match.
    """
    role_lower = role.lower()
    domain_keywords = {
        "frontend": "frontend",
        "backend": "backend",
        "database": "database",
        "db": "database",
        "devops": "devops",
        "qa": "qa",
        "security": "security",
        "design": "design",
        "ml": "ml",
        "data": "data",
    }
    for keyword, domain in domain_keywords.items():
        if keyword in role_lower:
            return domain
    return "general"


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
    """Node 3: Builds task DAG and dispatches independent tasks in parallel.

    Builds the task list with dependency analysis and persists state.
    Returns state update dict containing tasks list and current_phase execution.
    The conditional edge router _route_after_execution then dispatches the first wave
    of ready tasks via Send objects.
    """
    logger.info("execution_node_start", project_id=state["project_id"])

    brief = state.get("brief", {}) or {}
    team = state.get("team_composition", {}) or {}
    specialists = team.get("specialists", [])
    requirements = brief.get("functional_requirements", [])

    if not requirements:
        return {
            "tasks": [],
            "current_phase": "review",
            "messages": ["[execution] No requirements found. Moving to review."],
        }

    # Build task list with dependency analysis
    tasks: list[Task] = []
    for i, req in enumerate(requirements):
        # Assign round-robin across specialists
        assigned = (
            specialists[i % len(specialists)]["role"]
            if specialists
            else "general-specialist"
        )
        # Simple dependency: each task depends on the previous
        # Phase 4: tasks within same domain run in parallel,
        # cross-domain tasks respect ordering
        depends_on = []
        if i > 0:
            # Only depend on previous task if different specialist
            prev_assigned = (
                specialists[(i - 1) % len(specialists)]["role"]
                if specialists
                else "general-specialist"
            )
            if assigned == prev_assigned:
                depends_on = [f"T{i}"]

        task: Task = {
            "id": f"T{i + 1}",
            "description": req,
            "assigned_to": assigned,
            "depends_on": depends_on,
            "status": TaskStatus.PENDING,
            "result": None,
            "error": None,
            "attempts": 0,
            "started_at": None,
            "completed_at": None,
        }
        tasks.append(task)

    updates = {
        "tasks": tasks,
        "current_phase": "execution",
        "messages": [f"[execution] DAG built: {len(tasks)} tasks."],
    }
    save_project_state({**state, **updates})
    return updates


def review_node(state: ProjectState) -> dict:
    """Node 4: Assembles task results, writes project summary to vault, triggers
    Memory Manager distillation.
    """
    from neuroforge.workflows.task_store import load_all_task_results
    from neuroforge.workflows.vault_writer import write_project_summary

    logger.info("review_node_start", project_id=state["project_id"])
    project_id = state["project_id"]

    # Assemble all task results
    task_results = load_all_task_results(project_id)
    completed = state.get("completed_task_ids", [])
    failed = state.get("failed_task_ids", [])

    # Write project summary to vault
    write_project_summary(
        project_id=project_id,
        goal=state.get("raw_goal", ""),
        brief=state.get("brief", {}) or {},
        task_results=task_results,
        completed_task_ids=completed,
        failed_task_ids=failed,
    )

    # Trigger Memory Manager if tasks ran
    surface_items = []
    if task_results:
        surface_items = _run_memory_distillation(
            project_id=project_id, state=state, task_results=task_results
        )

    phase = "complete" if not failed else "complete_with_failures"
    updates = {
        "current_phase": phase,
        "messages": [
            f"[review] Project complete. "
            f"Tasks: {len(completed)} done, {len(failed)} failed. "
            f"Memory distilled. "
            f"Human review items: {len(surface_items)}."
        ],
    }
    save_project_state({**state, **updates})
    return updates


def _run_memory_distillation(
    project_id: str, state: dict, task_results: dict
) -> list:
    """Runs Memory Manager at project close.

    Returns list of items to surface to human. Silent on failure — memory
    distillation is best-effort.
    """
    try:
        from neuroforge.agents.base import AgentInput
        from neuroforge.agents.memory_manager_agent import MemoryManagerAgent

        # Build operational events from task results
        events = []
        for task_id, result in task_results.items():
            events.append(
                {
                    "task_id": task_id,
                    "status": result.get("status", "unknown"),
                    "summary": result.get("summary", ""),
                    "decisions": result.get("decisions_made", []),
                    "blockers": result.get("blockers", []),
                }
            )

        agent = MemoryManagerAgent()
        output = agent.run(
            AgentInput(task=json.dumps(events), project_id=project_id)
        )

        if output.success:
            return output.result.get("surface_to_human", [])
        return []
    except Exception as e:
        logger.warning(
            "memory_distillation_failed", project_id=project_id, error=str(e)
        )
        return []


def _route_after_task(state: ProjectState) -> str | list:
    """Conditional edge after each task completes.

    Checks if any newly unblocked tasks are ready to run.
    Only dispatches tasks whose dependencies are ALL satisfied AND
    which have at least one non-empty dependency (first-wave independent tasks
    are dispatched solely by _route_after_execution).
    If all tasks complete or no progress can be made, routes to review.
    """
    completed = set(state.get("completed_task_ids", []))
    failed = set(state.get("failed_task_ids", []))
    tasks = state.get("tasks", [])

    all_task_ids = {t["id"] for t in tasks}
    remaining = all_task_ids - completed - failed

    # Check if all done
    if not remaining:
        return "review"

    # Find newly unblocked dependent tasks
    ready = [
        t
        for t in tasks
        if t["id"] in remaining
        and t["depends_on"]
        and all(dep in completed for dep in t["depends_on"])
    ]

    if ready:
        # Dispatch next wave in parallel
        return [
            Send(
                "execute_single_task",
                {
                    "project_id": state["project_id"],
                    "task": task,
                    "brief": state.get("brief", {}),
                    "team_composition": state.get("team_composition", {}),
                    "attempt": 0,
                },
            )
            for task in ready
        ]

    # Tasks remain but none are ready or remaining tasks are waiting
    return "review"


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


def _route_after_execution(state: ProjectState) -> str | list:
    """Conditional edge: where to go after execution node.

    Dispatches ready tasks (no unmet dependencies) in parallel via Send.
    If no tasks exist, routes to review.
    """
    if state.get("current_phase") == "failed":
        return "end"

    tasks = state.get("tasks", [])
    completed = set(state.get("completed_task_ids", []))
    failed = set(state.get("failed_task_ids", []))
    all_task_ids = {t["id"] for t in tasks}
    remaining = all_task_ids - completed - failed

    ready = [
        t
        for t in tasks
        if t["id"] in remaining
        and all(dep in completed for dep in t["depends_on"])
    ]

    if ready:
        return [
            Send(
                "execute_single_task",
                {
                    "project_id": state["project_id"],
                    "task": task,
                    "brief": state.get("brief", {}),
                    "team_composition": state.get("team_composition", {}),
                    "attempt": 0,
                },
            )
            for task in ready
        ]

    return "review"
