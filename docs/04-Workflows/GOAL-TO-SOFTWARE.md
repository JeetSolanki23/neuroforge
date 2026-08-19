# Workflow: Goal to Software

tags: #workflow #end-to-end

---

## The Complete Flow

This is what happens from the moment you type a goal to the moment you have working software.

---

### Phase 1 — Goal Intake (CEO)

```
Human inputs: "Build me a REST API for a todo app with JWT auth and PostgreSQL"

CEO Agent:
  1. Parses goal into structured format
  2. Queries memory: "any similar past projects?"
     → Found: "django-rest-api-with-jwt" project from 3 months ago
     → Loads relevant learnings (JWT refresh race condition fix, etc.)
  3. Identifies any ambiguities:
     → "Which Python framework?" — not specified
     → CEO adds to brief: "framework TBD by Backend Lead"
  4. Assesses scope: SMALL (single API, one domain)
  5. Produces Project Brief

Output: Project Brief → Project Manager
```

---

### Phase 2 — Team Formation

```
Project Manager receives brief
    ↓
Project Manager → HR Agent: "Compose team for this brief"
    ↓
HR Agent:
  1. Reads brief: scope = SMALL → no Team Leads needed
  2. Determines needed agents:
     → backend-django-specialist (or fastapi, TBD by lead)
     → database-postgresql-specialist
     → security-audit-specialist
     → qa-pytest-specialist
  3. Checks Resource Manager: all available
  4. Proposes team to Project Manager
    ↓
Project Manager → CEO: "Proposed team: [list]"
    ↓
CEO reviews:
  → All agent types exist in registry ✓
  → No new agent types needed ✓
  → Approves team
    ↓
Project Manager → Prompt Engineer: "Configure these agents for this project"
    ↓
Prompt Engineer:
  1. Loads base definitions from registry
  2. Injects project-specific context into each prompt
  3. Returns configured agent instances
    ↓
Tool Maker: checks all required tools are available → confirms
    ↓
Memory Manager: prepares context packets with relevant past knowledge
    ↓
Team is ready
```

---

### Phase 3 — Project Brief → Task DAG

```
Project Manager builds DAG:

T1: database-postgresql-specialist → "Design schema: users, todos tables"
T2: backend-django-specialist → "Set up Django project, install deps" (no deps)
T3: backend-django-specialist → "Build /api/auth/register endpoint" (deps: T1, T2)
T4: backend-django-specialist → "Build /api/auth/token endpoint" (deps: T1, T2)
T5: backend-django-specialist → "Build /api/todos CRUD endpoints" (deps: T1, T2)
T6: security-audit-specialist → "Audit auth implementation" (deps: T3, T4)
T7: qa-pytest-specialist → "Write and run test suite" (deps: T3, T4, T5)
T8: qa-pytest-specialist → "Run final test suite" (deps: T6, T7)

Parallelism: T1 and T2 run simultaneously
             T3, T4, T5 run simultaneously once T1+T2 done
             T6 and T7 run simultaneously
```

---

### Phase 4 — Execution

```
Project Manager dispatches T1 and T2 simultaneously:
    ↓
database-postgresql-specialist executes T1:
  → Designs schema
  → Writes migration files
  → Reports complete → output: schema.sql, migration files
    ↓
backend-django-specialist executes T2:
  → Sets up Django project
  → Installs requirements
  → Configures settings
  → Reports complete
    ↓
T1 + T2 complete → T3, T4, T5 unblocked → dispatched simultaneously
    ↓
[T3 — auth register endpoint]:
  → Reads schema from T1 output
  → Reads memory context: "JWT refresh tokens need 5-min overlap"
  → Implements endpoint
  → Runs unit tests
  → Reports complete
    ↓
[T4 — auth token endpoint]: same pattern, parallel
[T5 — todos CRUD]: same pattern, parallel
    ↓
All complete → T6 and T7 unblocked
    ↓
[T6 — security audit]:
  → Reviews auth implementation
  → Finds: token expiry not set on refresh tokens
  → Reports: BLOCKED — needs fix before sign-off
    ↓
Project Manager: reassigns fix to backend-django-specialist
  → Fix applied → T6 resumes → passes audit
    ↓
[T7 — test suite]: runs, all pass
    ↓
T8: final test suite → all pass → project complete
```

---

### Phase 5 — Project Close

```
Project Manager: confirms all tasks complete
    ↓
Memory Manager: produces end-of-project report
  Learnings distilled:
    1. "Token expiry on refresh tokens: easy to miss, must be in default checklist"
    2. "Django project setup T estimated 20min, actual 8min — update estimates"
    3. "security-audit-specialist caught refresh token bug — high value, use on all auth projects"
    ↓
Memory Manager → CEO: "3 learnings, 1 flagged for review"
    ↓
CEO reviews:
  → Learning 1 (refresh token checklist): "Surface to human? Yes — affects future projects significantly"
  → Learning 2 (time estimates): "No human review needed — auto-update"
  → Learning 3 (security agent value): "No human review needed — auto-note"
    ↓
CEO → Human: "Project complete. One learning flagged: [refresh token detail]"
    ↓
Human reviews and confirms
    ↓
Prompt Engineer: updates backend agent default checklist (CEO approves)
All entries written to vault and ChromaDB
Project archived
```

---

## Timing Summary (estimated for a small project like above)

| Phase | Who | Estimated time |
|---|---|---|
| Goal intake + brief | CEO | 2-3 min |
| Team formation + approval | HR + CEO | 3-5 min |
| DAG construction | Project Manager | 1-2 min |
| Execution (with parallelism) | Specialist agents | 20-40 min |
| QA + security audit | QA + Security agents | 10-15 min |
| Project close + memory | Memory Manager + CEO | 5 min |
| **Total** | | **~45-65 min** |

---

## Related Notes

- [[../02-Agents/CEO-ORCHESTRATOR]]
- [[../02-Agents/PROJECT-MANAGER]]
- [[AGENT-CREATION]]
- [[FAILURE-RECOVERY]]
- [[EVOLUTION-CYCLE]]
