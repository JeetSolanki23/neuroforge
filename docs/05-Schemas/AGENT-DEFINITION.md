# Schema: Agent Definition

tags: #schema #agents #registry

---

## Overview

The agent definition is the canonical record of an agent type. It is the blueprint from which every instance of that agent is created. It is versioned, searchable, and evolved over time.

---

## Full Schema

```json
{
  "schema_version": "1.0",

  "id": "backend-django-specialist",
  "version": "1.2.0",
  "created_by": "prompt-engineer-agent",
  "created_at": "2024-01-15T10:30:00Z",
  "last_updated": "2024-03-22T14:15:00Z",
  "update_reason": "auto-refinement",
  "update_approved_by": "ceo-agent",

  "identity": {
    "name": "Backend Django Specialist",
    "role": "Implements Python/Django REST APIs, handles DB interactions, auth, and business logic",
    "domain": "backend",
    "layer": "dynamic",
    "scope": "execution"
  },

  "prompt": {
    "system_prompt": "You are a Backend Django Specialist...[full prompt text]",
    "examples": [
      {
        "task": "Build a user registration endpoint",
        "good_response": "...",
        "explanation": "Shows input validation, error handling, correct status codes"
      }
    ]
  },

  "capabilities": {
    "tools": [
      "file_read",
      "file_write",
      "run_python",
      "run_tests",
      "git_commit",
      "pip_install"
    ],
    "can_spawn_agents": false,
    "can_write_memory": false,
    "can_request_tools": true,
    "memory_access": "read-only via Memory Manager"
  },

  "constraints": {
    "must_not": [
      "Write to database without a migration file",
      "Store passwords in plain text",
      "Ignore input validation",
      "Commit directly to main branch"
    ],
    "must_always": [
      "Add docstrings to all views and serializers",
      "Return standard error format: {error: string, code: int}",
      "Check JWT refresh token expiry explicitly (not inherited from access token)",
      "Run tests before reporting task complete"
    ],
    "escalate_if": [
      "Schema ambiguity blocks implementation",
      "Security vulnerability identified",
      "Task estimated complexity is 2x+ original estimate",
      "Dependency conflict cannot be resolved"
    ]
  },

  "performance": {
    "projects_used_in": 4,
    "tasks_completed": 23,
    "tasks_failed": 1,
    "tasks_escalated": 2,
    "success_rate": 0.956,
    "average_task_duration_minutes": 11.3,
    "common_failure_modes": [
      "JWT refresh token expiry not set (fixed in v1.1.0)"
    ],
    "last_performance_review": "2024-03-22T14:00:00Z"
  },

  "evolution_log": [
    {
      "version": "1.0.0",
      "date": "2024-01-15",
      "type": "initial_creation",
      "approved_by": "human",
      "summary": "Initial creation by Prompt Engineer for todo-api project"
    },
    {
      "version": "1.1.0",
      "date": "2024-02-08",
      "type": "auto-refinement",
      "approved_by": "ceo-agent",
      "summary": "Added JWT refresh expiry to must_always checklist (LK-2024-031)"
    },
    {
      "version": "1.2.0",
      "date": "2024-03-22",
      "type": "auto-refinement",
      "approved_by": "ceo-agent",
      "summary": "Updated example to show correct DRF serializer error handling"
    }
  ],

  "related_knowledge": [
    "LK-2024-031",
    "LK-2024-044"
  ],

  "tags": ["backend", "python", "django", "rest-api", "postgresql"]
}
```

---

## Versioning Rules

Semantic versioning: `MAJOR.MINOR.PATCH`

| Change type | Version bump | Approval |
|---|---|---|
| Bug fix in prompt (wording error, wrong instruction) | PATCH | CEO |
| Prompt refinement (new checklist item, better example) | MINOR | CEO |
| New tool added or removed | MINOR | CEO |
| New constraint added | MINOR | CEO |
| Constraint removed or relaxed | MAJOR | **Human** |
| Fundamental role change | MAJOR | **Human** |
| New agent type created from scratch | v1.0.0 | **Human** |

---

## How It Gets Used

```python
# Loading an agent definition (pseudocode)
definition = agent_registry.load("backend-django-specialist", version="latest")

# Configuring for a specific project
instance = definition.instantiate(
    project_brief=brief,
    memory_context=memory_manager.get_context("backend-django-specialist", brief),
    assigned_tools=definition.capabilities.tools,
    task=current_task
)
```

---

## Storage Locations

**ChromaDB:** `agent_definitions` collection
- Document: full JSON schema
- Metadata: id, version, domain, tags, success_rate
- Embedding: generated from role + system_prompt (for semantic search)

**Markdown Vault:** `memory-vault/agents/{id}/v{version}.md`
- Human-readable version of the same data
- Linked in Obsidian graph view

---

## Related Notes

- [[../02-Agents/DYNAMIC-AGENTS]]
- [[../02-Agents/BOOTSTRAP-CORE]]
- [[../04-Workflows/EVOLUTION-CYCLE]]
- [[PROJECT-BRIEF]]
