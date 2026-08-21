from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from neuroforge.schemas.base import ProjectScope, ProjectStatus


class TaskStatus:
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETE = "complete"
    FAILED = "failed"
    BLOCKED = "blocked"


class Task(TypedDict):
    id: str  # e.g. "T1", "T2"
    description: str  # what to do
    assigned_to: str  # agent_id
    depends_on: list[str]  # list of task ids that must complete first
    status: str  # TaskStatus value
    result: str | None  # output from agent, None until complete
    error: str | None  # error message if failed
    attempts: int  # retry count
    started_at: str | None  # ISO timestamp
    completed_at: str | None  # ISO timestamp


class ProjectState(TypedDict):
    # Project identity
    project_id: str
    raw_goal: str

    # Brief (produced by CEO node)
    brief: dict | None

    # Team (produced by HR node)
    team_composition: dict | None
    team_approved: bool

    # Task DAG (built by Project Manager node)
    tasks: list[Task]

    # Execution tracking
    current_phase: (
        str  # "briefing"|"team_formation"|"execution"|"review"|"complete"|"failed"
    )
    completed_task_ids: Annotated[list[str], operator.add]  # append-only
    failed_task_ids: Annotated[list[str], operator.add]  # append-only

    # Messages / log (append-only for audit trail)
    messages: Annotated[list[str], operator.add]

    # Final output
    error: str | None
    needs_human_input: bool
    human_input_reason: str | None
