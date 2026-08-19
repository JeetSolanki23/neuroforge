# Schema: Memory Entry

tags: #schema #memory #knowledge

---

## Overview

Memory entries are what the Memory Manager writes to ChromaDB and the markdown vault after distilling project experience. There are two entry types: **learned knowledge** (permanent, cross-project insights) and **operational events** (temporary, per-project logs).

---

## Learned Knowledge Entry

Permanent. Written at project close (or mid-project trigger). Represents a distilled insight transferable to future projects.

```json
{
  "schema_version": "1.0",

  "id": "LK-2024-031",
  "type": "learned_knowledge",
  "created_by": "memory-manager-agent",
  "created_at": "2024-02-08T16:00:00Z",
  "approved_by": "ceo-agent",

  "title": "JWT refresh tokens require explicit expiry — easy to miss",

  "content": "Refresh tokens in djangorestframework-simplejwt do not inherit the ACCESS_TOKEN_LIFETIME setting. REFRESH_TOKEN_LIFETIME must be set explicitly in SIMPLE_JWT config or refresh tokens will not expire, creating a permanent session vulnerability.",

  "domain": ["backend", "auth", "security"],

  "applies_to_agents": [
    "backend-django-specialist",
    "backend-fastapi-specialist",
    "backend-node-specialist",
    "security-audit-specialist"
  ],

  "evidence": {
    "project_ids": ["project-todo-api-001"],
    "occurrence_count": 1,
    "confidence": "medium"
  },

  "action_taken": {
    "agent_updated": "backend-django-specialist",
    "version_before": "1.0.0",
    "version_after": "1.1.0",
    "change": "Added explicit refresh token expiry to must_always checklist"
  },

  "tags": ["jwt", "auth", "django", "security", "refresh-token"],

  "surfaced_to_human": true,
  "human_acknowledged_at": "2024-02-08T17:30:00Z"
}
```

---

## Operational Event Entry

Temporary. Written continuously during a project. Raw, detailed, time-stamped. Purged 90 days after project close.

```json
{
  "schema_version": "1.0",

  "id": "OP-project-todo-api-001-0042",
  "type": "operational_event",
  "project_id": "project-todo-api-001",
  "timestamp": "2024-03-25T10:34:12Z",

  "event_type": "task_failure | task_success | escalation | decision | tool_call | retry | agent_blocked",

  "agent_id": "backend-django-specialist-03",
  "task_id": "T3",

  "summary": "Task T3 failed on first attempt — JWT refresh expiry not set",
  "detail": "Agent produced /api/auth/token endpoint but did not set REFRESH_TOKEN_LIFETIME. Security agent flagged in T6. backend-django-specialist-03 reassigned to fix. Fix applied in 8 minutes.",

  "resolution": "fixed_on_retry",
  "layers_reached": 1,

  "tags": ["jwt", "auth", "failure", "layer-1-retry"]
}
```

---

## Confidence Levels

| Level | Meaning | Occurrence count |
|---|---|---|
| `low` | Seen once, could be coincidence | 1 |
| `medium` | Seen 2–3 times, likely a pattern | 2–3 |
| `high` | Seen 4+ times, definite pattern | 4+ |
| `confirmed` | Human explicitly validated | Any |

---

## What Gets Promoted to Learned Knowledge

The Memory Manager evaluates operational events at project close and promotes entries that meet at least one of these criteria:

- A failure occurred that isn't already in learned knowledge
- A decision was made that resolved a recurring ambiguity
- A pattern appeared 3+ times within the project
- A tech decision has a clear outcome (good or bad) worth recording
- A new agent or tool performed notably well or poorly

Routine successes with no novel outcome are **not** promoted.

---

## ID Conventions

```
Learned knowledge:   LK-{YYYY}-{NNN}        e.g. LK-2024-031
Operational event:   OP-{project-id}-{NNN}  e.g. OP-project-todo-api-001-0042
```

---

## Related Notes

- [[../03-Memory/MEMORY-ARCHITECTURE]]
- [[../02-Agents/BOOTSTRAP-CORE]]
- [[../04-Workflows/EVOLUTION-CYCLE]]
- [[AGENT-DEFINITION]]
- [[TOOL-DEFINITION]]
