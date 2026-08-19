# Dynamic Agents

tags: #agent #dynamic #execution

---

## What Dynamic Agents Are

Dynamic agents are the builders — the ones that actually write code, run tests, configure infrastructure, and produce deliverables. They are created on demand for each project. Their definitions are saved and improved over time.

---

## Lifecycle

```
HR Agent requests agent type
    ↓
Check agent registry in memory
    ├── Agent type exists → load definition → configure for project context
    └── Agent type does NOT exist → Prompt Engineer writes new definition
                                        → Human approves (Option C)
                                        → Save to registry → configure for project
    ↓
Resource Manager checks availability
    ├── Idle instance exists → assign to project
    └── No idle instance → spawn new instance from definition
    ↓
Agent receives context packet from Team Lead / Project Manager
    ↓
Agent executes tasks → reports back → logs to Memory Manager
    ↓
Project closes → agent instance decommissioned
    ↓
Definition stays in registry (improved by Prompt Engineer if warranted)
```

---

## Agent Registry

Every agent type that has ever been created is stored in the registry as a versioned [[../05-Schemas/AGENT-DEFINITION|Agent Definition]]. This means:

- A "Backend Django Specialist" built for Project 1 is available for Project 5 without rebuilding
- Each version carries performance history so HR Agent can make smart selections
- Definitions improve between projects based on learnings

---

## Common Agent Types (built up over time)

These don't exist at day one — they accumulate as you use the system:

**Frontend:**
- `frontend-react-specialist` — React components, hooks, state management
- `frontend-vue-specialist` — Vue 3 composition API
- `frontend-css-specialist` — Tailwind, CSS Modules, responsive design

**Backend:**
- `backend-django-specialist` — Django REST Framework, ORM, migrations
- `backend-fastapi-specialist` — FastAPI, Pydantic, async patterns
- `backend-node-specialist` — Express/Node, middleware, JWT

**Database:**
- `database-postgresql-specialist` — schema design, migrations, query optimization
- `database-mongodb-specialist` — document modeling, aggregation pipelines

**DevOps:**
- `devops-github-actions-specialist` — CI/CD workflows, testing gates
- `devops-docker-specialist` — Dockerfiles, compose, multi-stage builds

**QA:**
- `qa-pytest-specialist` — unit and integration testing in Python
- `qa-playwright-specialist` — end-to-end browser testing

**Security:**
- `security-audit-specialist` — OWASP checks, dependency scanning, auth review

---

## What Happens When a Needed Agent Type Doesn't Exist

```
Team Lead or Project Manager identifies need for unknown agent type
    ↓
Escalate to CEO via Project Manager
    ↓
CEO evaluates: is this genuinely new, or a variation of existing?
    ├── Variation → Prompt Engineer customises existing definition
    └── Genuinely new → CEO flags to human for approval
            ↓
        Human approves
            ↓
        Prompt Engineer writes new definition from scratch
        Tool Maker checks if new tools are needed
            ↓
        Definition saved to registry
            ↓
        Agent spawned, project continues
```

---

## What Each Specialist Agent Receives

Every specialist agent gets a context packet — not just a bare task. The Team Lead is responsible for curating the right slice:

```json
{
  "my_identity": "backend-django-specialist",
  "my_task": "Build /api/auth/token endpoint with JWT",
  "project_brief_summary": "SaaS task manager, Django + React, PostgreSQL",
  "decisions_that_affect_me": {
    "database": "PostgreSQL, UUID primary keys, tables defined in T1",
    "auth": "JWT tokens, 24hr expiry, refresh tokens stored in DB"
  },
  "constraints": [
    "Must not break existing /api/users endpoint",
    "Input validation required on all endpoints",
    "Return standard error format: {error: string, code: int}"
  ],
  "available_tools": ["file_read", "file_write", "run_tests", "git_commit"],
  "escalate_if": [
    "Schema ambiguity blocks implementation",
    "Security concern identified",
    "Task estimated >2x original complexity"
  ],
  "memory_context": [
    "Past project: JWT refresh race condition fixed by 5-min overlap window"
  ]
}
```

---

## Related Notes

- [[BOOTSTRAP-CORE]]
- [[TEAM-LEAD]]
- [[../05-Schemas/AGENT-DEFINITION]]
- [[../04-Workflows/AGENT-CREATION]]
