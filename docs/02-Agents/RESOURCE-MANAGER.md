# Resource Manager Agent

tags: #agent #management #layer-2 #permanent

---

## Role Summary

The Resource Manager is the only agent with a global view of all active projects simultaneously. While each Project Manager knows only its own project, the Resource Manager tracks every agent instance across every running project and makes capacity decisions so the CEO and Project Managers never have to think about availability.

It is a permanent agent — like the bootstrap core, it always runs and is never deleted.

---

## Core Responsibility

When HR Agent asks "I need a `backend-django-specialist` for Project X," the Resource Manager answers one of three ways:

- "Here's an idle instance — assign it"
- "No idle instance exists — spawning a new one now"
- "No idle instance, project is queued — estimated wait: N minutes"

That's it. Everything else flows from this.

---

## What It Tracks

A live registry of every agent instance currently in the system:

```json
{
  "instance_id": "backend-django-specialist-03",
  "agent_type": "backend-django-specialist",
  "agent_version": "1.2.0",
  "status": "active | idle | queued | decommissioning",
  "current_project": "project-todo-api-001",
  "current_task": "T3",
  "assigned_since": "2024-03-25T09:45:00Z",
  "projects_completed": 4,
  "average_task_duration_minutes": 11.3,
  "last_active": "2024-03-25T10:12:00Z"
}
```

---

## Responsibilities

### Agent availability management
- Maintain live status of all agent instances
- Mark instances idle when their task completes
- Mark instances active when assigned to a task
- Decommission instances when their project closes and no queue is waiting

### Instance spawning
- Spawn new instances from agent definitions when no idle instance is available
- Always spawn from the latest version of an agent definition
- Register new instances immediately in the live registry

### Queuing
- When an agent type is fully occupied and project priority doesn't justify a new instance: queue the request
- Notify Project Manager of estimated wait time
- Auto-assign queued requests when an instance becomes idle

### Performance tracking
- Record task duration per instance
- Aggregate into performance metrics that feed back to Memory Manager
- Flag instances with abnormally high failure or escalation rates

### Cross-project load reporting
- Periodically report overall system load to CEO
- Flag if system is consistently at capacity (signal to consider raising instance limits)

---

## Spawning Decision Logic

```
New agent instance requested:
    ↓
Check: idle instance of this type exists?
    ├── YES → assign it → done
    └── NO  →
            Check: is this project HIGH priority?
                ├── YES → spawn new instance immediately
                └── NO  →
                        Check: active instance count < MAX_INSTANCES?
                            ├── YES → spawn new instance
                            └── NO  → queue request, notify Project Manager
```

**Default MAX_INSTANCES per agent type:** 3 (configurable, see [[../06-Decisions/OPEN-QUESTIONS]] OQ-002)

---

## What It Does NOT Do

- Does not assign tasks to agents (Project Manager / Team Lead does that)
- Does not write agent definitions (Prompt Engineer does that)
- Does not decide which project gets priority (CEO does that)
- Does not write to memory directly (Memory Manager does that)

---

## Relationship With Other Agents

| Agent | Relationship |
|---|---|
| HR Agent | HR requests agents; Resource Manager fulfils or queues |
| Project Manager | Notified of wait times and instance availability |
| CEO | Receives load reports; sets priority signals |
| Memory Manager | Receives performance data for cross-project tracking |

---

## Decommission Flow

When a project closes:

```
Project Manager signals project complete
    ↓
Resource Manager:
    For each agent instance assigned to this project:
        ├── Is this instance type in the queue?
        │     YES → reassign instance to queued project immediately
        └── NO  → mark instance idle (keep alive for 30min)
                      → no new assignment in 30min → decommission
```

Idle instances are kept briefly to avoid spawn overhead for back-to-back projects.

---

## Related Notes

- [[PROJECT-MANAGER]]
- [[../01-Architecture/AGENT-HIERARCHY]]
- [[../04-Workflows/GOAL-TO-SOFTWARE]]
- [[../06-Decisions/OPEN-QUESTIONS]]
