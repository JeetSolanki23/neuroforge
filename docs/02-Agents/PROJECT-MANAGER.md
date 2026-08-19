# Project Manager & Resource Manager Agents

tags: #agent #management #layer-2

---

## Project Manager Agent

### Role
The CEO's delegate for a single project. Once the CEO hands over a Project Brief and approves the team, the Project Manager owns everything from that point until the project closes. The CEO hears from it only when a human-level decision is needed.

### One Project Manager per active project
Multiple projects run in parallel. Each gets its own Project Manager instance. They do not communicate with each other — that cross-project coordination is the Resource Manager's job.

### Responsibilities

**On project start:**
- Receive Project Brief from CEO
- Work with HR Agent to propose team composition
- Once CEO approves team, coordinate with Prompt Engineer and Tool Maker to configure agents
- Build the project's task DAG (Directed Acyclic Graph)
- Dispatch tasks to Team Leads (or directly to agents on small projects)

**During execution:**
- Track all task statuses in the DAG
- Receive status reports from Team Leads
- Unblock agents when dependencies are resolved
- Resolve conflicts within the project (two agents touching the same file, contradicting decisions)
- Escalate to CEO only when unresolvable

**On project close:**
- Confirm all tasks complete and QA passed
- Trigger Memory Manager end-of-project report
- Report project outcome to CEO
- Archive project state

### What Project Manager does NOT do
- Does not talk to individual specialist agents (goes through Team Leads on medium/large projects)
- Does not track availability of agents across other projects (Resource Manager)
- Does not write agent prompts or tools
- Does not write to memory directly (Memory Manager does)

### Task DAG structure
```
{
  "project_id": "string",
  "tasks": [
    {
      "id": "T1",
      "assigned_to": "team_lead_backend",
      "description": "Design database schema",
      "status": "pending | active | blocked | complete | failed",
      "depends_on": [],
      "outputs": [],
      "started_at": null,
      "completed_at": null
    },
    {
      "id": "T2",
      "assigned_to": "team_lead_frontend",
      "description": "Build login UI",
      "status": "pending",
      "depends_on": ["T1"],
      "outputs": [],
      ...
    }
  ]
}
```

### Failure handling (layered)
```
Task fails →
  1. Retry (up to 3 times, same agent)
  2. Reassign (different agent instance, same type)
  3. Re-plan (decompose task differently, back to DAG)
  4. Escalate to CEO (if still unresolvable)
```

---

## Resource Manager Agent

### Role
Global capacity tracker. While each Project Manager knows only its own project, the Resource Manager sees across all active projects and manages agent availability.

### Responsibilities
- Maintain a live map of all active agent instances and their current tasks
- When HR Agent requests agents for a new project: check availability
- If requested agent type is busy: decide whether to queue, spawn new instance, or report constraint to CEO
- Track agent performance metrics across projects (feeds into Memory Manager)
- Decommission agent instances when projects close

### Spawning policy
```
Agent requested for new project:
  → Check if idle instance exists → assign it
  → No idle instance + project is high priority → spawn new instance
  → No idle instance + project is normal priority → queue until available
  → Persistent overload → report to CEO (may need to surface to human)
```

### What it tracks
```json
{
  "agent_id": "backend-django-specialist-01",
  "type": "backend-django-specialist",
  "status": "active | idle | queued",
  "current_project": "project-id or null",
  "current_task": "task-id or null",
  "projects_completed": 4,
  "average_task_duration_minutes": 12
}
```

---

## How They Work Together

```
CEO issues Project Brief
    ↓
Project Manager receives brief
    ↓
Project Manager → asks HR Agent for team proposal
    ↓
HR Agent → asks Resource Manager for availability
    ↓
Resource Manager → returns available agents / constraints
    ↓
HR Agent → builds team proposal
    ↓
Project Manager → sends proposal to CEO for approval
    ↓
CEO approves
    ↓
Project Manager → begins project execution
```

---

## Related Notes

- [[CEO-ORCHESTRATOR]]
- [[TEAM-LEAD]]
- [[../04-Workflows/GOAL-TO-SOFTWARE]]
- [[../04-Workflows/FAILURE-RECOVERY]]
