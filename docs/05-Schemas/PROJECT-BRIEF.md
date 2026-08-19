# Schema: Project Brief

tags: #schema #project #ceo

---

## Overview

The Project Brief is produced by the CEO after parsing the human's goal. It is the single source of truth for the entire project. Every agent reads it. No agent works from the raw human input — they all work from the brief.

---

## Full Schema

```json
{
  "schema_version": "1.0",

  "id": "project-todo-api-001",
  "created_by": "ceo-agent",
  "created_at": "2024-03-25T09:00:00Z",
  "status": "active | complete | archived | cancelled",

  "goal": {
    "raw_input": "Build me a REST API for a todo app with JWT auth and PostgreSQL",
    "parsed_intent": "Create a production-ready REST API for todo management with JWT-based authentication, using Django/FastAPI and PostgreSQL",
    "ambiguities_identified": [
      "Python framework not specified — resolved: Backend Lead decides"
    ],
    "ambiguities_resolved_how": "delegated-to-lead"
  },

  "scope": {
    "size": "small | medium | large",
    "estimated_complexity": "low | medium | high",
    "domains_involved": ["backend", "database", "security", "qa"],
    "estimated_duration_hours": 1,
    "requires_team_leads": false
  },

  "requirements": {
    "functional": [
      "User registration and login",
      "JWT token issuance and refresh",
      "Todo CRUD operations (create, read, update, delete)",
      "Todos scoped to authenticated user only"
    ],
    "non_functional": [
      "Input validation on all endpoints",
      "Standard error response format",
      "Test coverage > 80%"
    ],
    "explicitly_excluded": [],
    "open_decisions": [
      "Python framework (Django vs FastAPI) — Backend Lead decides"
    ]
  },

  "constraints": {
    "tech": [],
    "integration": [],
    "cost": [],
    "timeline": null,
    "other": []
  },

  "acceptance_criteria": [
    "All CRUD endpoints return correct HTTP status codes",
    "Auth endpoints issue and validate JWT correctly",
    "Refresh token expiry is explicitly set",
    "All tests pass",
    "Security audit passes"
  ],

  "memory_context": {
    "similar_past_projects": ["project-auth-api-2024-001"],
    "relevant_learnings": ["LK-2024-031"],
    "notes": "Past project had JWT refresh expiry issue — added to acceptance criteria"
  },

  "team": {
    "project_manager": "pm-agent-instance-07",
    "team_leads": [],
    "specialists": [
      "backend-django-specialist-instance-03",
      "database-postgresql-specialist-instance-01",
      "security-audit-specialist-instance-02",
      "qa-pytest-specialist-instance-04"
    ],
    "approved_by": "ceo-agent",
    "approved_at": "2024-03-25T09:08:00Z"
  }
}
```

---

## How It Gets Used

Every agent gets the brief (or relevant sections) in their context packet. It answers the questions agents would otherwise have to ask:

- What am I building?
- What are the hard requirements?
- What can I decide on my own?
- How do I know when I'm done?

---

## Related Notes

- [[../02-Agents/CEO-ORCHESTRATOR]]
- [[../04-Workflows/GOAL-TO-SOFTWARE]]
- [[AGENT-DEFINITION]]
- [[MEMORY-ENTRY]]
