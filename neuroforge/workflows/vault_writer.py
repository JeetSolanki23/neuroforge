from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from neuroforge.config import config
from neuroforge.logger import get_logger

logger = get_logger("vault_writer")


def write_project_summary(
    project_id: str,
    goal: str,
    brief: dict,
    task_results: dict[str, dict],
    completed_task_ids: list[str],
    failed_task_ids: list[str],
) -> bool:
    """Writes project outcome to markdown vault.

    Path: {MEMORY_VAULT_PATH}/projects/{project_id}/outcomes.md Returns True on
    success, False on failure (silent).
    """
    try:
        vault_path = Path(config.MEMORY_VAULT_PATH)
        project_dir = vault_path / "projects" / project_id
        project_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc)
        scope = brief.get("scope", "unknown")
        parsed_intent = brief.get("parsed_intent", goal)

        # Build task summary section
        task_lines = []
        for task_id in sorted(task_results.keys()):
            result = task_results[task_id]
            status = result.get("status", "unknown")
            summary = result.get("summary", "No summary")
            icon = "✓" if status == "complete" else "✗"
            task_lines.append(f"- {icon} **{task_id}**: {summary[:120]}")

        tasks_section = "\n".join(task_lines) if task_lines else "No tasks ran."

        # Build decisions section
        all_decisions = []
        for result in task_results.values():
            all_decisions.extend(result.get("decisions_made", []))
        decisions_section = (
            "\n".join(f"- {d}" for d in all_decisions)
            if all_decisions
            else "No significant decisions logged."
        )

        content = f"""---
project_id: {project_id}
goal: "{goal[:100]}"
scope: {scope}
completed: {now.strftime("%Y-%m-%d")}
tasks_done: {len(completed_task_ids)}
tasks_failed: {len(failed_task_ids)}
tags: [project, {scope}]
---

# Project: {parsed_intent[:80]}

**Goal:** {goal}
**Scope:** {scope}
**Completed:** {now.strftime("%Y-%m-%d %H:%M UTC")}

## Results

{tasks_section}

## Decisions Made

{decisions_section}

## Stats

| Metric | Value |
|---|---|
| Tasks completed | {len(completed_task_ids)} |
| Tasks failed | {len(failed_task_ids)} |
| Total tasks | {len(task_results)} |
"""
        filepath = project_dir / "outcomes.md"
        filepath.write_text(content, encoding="utf-8")

        # Also write brief.md if not already there
        brief_path = project_dir / "brief.md"
        if not brief_path.exists():
            write_project_brief(project_id, goal, brief)

        return True

    except Exception as e:
        logger.warning(
            "write_project_summary_failed", project_id=project_id, error=str(e)
        )
        return False


def write_project_brief(
    project_id: str,
    goal: str,
    brief: dict,
) -> bool:
    """Writes project brief to vault.

    Path: {MEMORY_VAULT_PATH}/projects/{project_id}/brief.md
    """
    try:
        vault_path = Path(config.MEMORY_VAULT_PATH)
        project_dir = vault_path / "projects" / project_id
        project_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc)
        requirements = brief.get("functional_requirements", [])
        criteria = brief.get("acceptance_criteria", [])
        constraints = brief.get("constraints", [])

        req_section = (
            "\n".join(f"- {r}" for r in requirements)
            if requirements
            else "None specified."
        )
        criteria_section = (
            "\n".join(f"- {c}" for c in criteria)
            if criteria
            else "None specified."
        )
        constraints_section = (
            "\n".join(f"- {c}" for c in constraints)
            if constraints
            else "None."
        )

        content = f"""---
project_id: {project_id}
goal: "{goal[:100]}"
scope: {brief.get("scope", "unknown")}
created: {now.strftime("%Y-%m-%d")}
tags: [project, brief, {brief.get("scope", "unknown")}]
---

# Brief: {brief.get("parsed_intent", goal)[:80]}

**Raw goal:** {goal}
**Scope:** {brief.get("scope", "unknown")}
**Created:** {now.strftime("%Y-%m-%d %H:%M UTC")}

## Functional Requirements

{req_section}

## Acceptance Criteria

{criteria_section}

## Constraints

{constraints_section}

## Reasoning

{brief.get("reasoning", "Not provided.")}
"""
        filepath = project_dir / "brief.md"
        filepath.write_text(content, encoding="utf-8")
        return True

    except Exception as e:
        logger.warning(
            "write_project_brief_failed", project_id=project_id, error=str(e)
        )
        return False
