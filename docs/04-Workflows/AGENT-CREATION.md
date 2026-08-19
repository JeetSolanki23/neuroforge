# Workflow: Agent Creation

tags: #workflow #agents #bootstrap

---

## When This Triggers

Agent creation fires when the HR Agent, building a team for a project, identifies that a required agent type does not exist in the registry.

---

## The Full Flow

```
HR Agent: team composition needed
    ↓
HR Agent queries agent registry
    ↓
Agent type found?
    ├── YES → load definition → configure for project → done
    └── NO  → begin creation flow below
```

### Step 1 — CEO evaluates the request

```
HR Agent → CEO: "Need [agent type], not in registry"
    ↓
CEO evaluates:
    ├── Is this a variation of an existing type?
    │     → Prompt Engineer customises existing definition
    │     → No human approval needed
    └── Is this genuinely new?
          → Begin new agent creation (requires human approval)
```

**Examples of "variation":**
- Need a "backend-fastapi-specialist" but only "backend-django-specialist" exists → customise
- Need a "qa-jest-specialist" but only "qa-pytest-specialist" exists → customise

**Examples of "genuinely new":**
- Need a "blockchain-solidity-specialist" — nothing in the backend or other domain covers this
- Need a "data-pipeline-specialist" — no ML/data agents exist yet

---

### Step 2 — Draft in parallel (don't block the project)

While the system waits for human approval on a new agent type, the bootstrap core drafts the definition so it's ready the moment approval comes:

```
Prompt Engineer: drafts system prompt and definition
Tool Maker: checks if any new tools are needed for this agent type
    → If new tools needed: drafts tool definitions too (also need human approval)
Memory Manager: queries for any relevant past knowledge to include
    ↓
Draft stored in registry with status: "pending_human_approval"
    ↓
Human notified: "New agent type requested: [name]. Review draft? [Y/N]"
```

The project continues with what it has. If the missing agent type is on the critical path, Project Manager marks those tasks as "pending" and continues parallel work.

---

### Step 3 — Human approval

```
Human receives notification with:
    - Agent type name and description
    - Proposed role and constraints
    - What project needs it
    - Whether new tools are also needed
    ↓
Human approves or rejects
    ├── APPROVED → agent activated → project continues
    └── REJECTED → CEO decides: descope that task, or find workaround
```

---

### Step 4 — First use and observation

New agents get extra monitoring on their first project:

```
Memory Manager: logs all new agent's actions with higher detail
Project Manager: checks new agent output before passing to downstream tasks
    → If output quality is low: flag to CEO immediately
    → If output quality is good: normal flow
    ↓
At project close: Memory Manager produces enhanced report for new agent
    → Prompt Engineer reviews and refines if needed
    → CEO approves refinement
```

---

## What Gets Created

A complete agent type package:

| Artifact | Created by | Stored in |
|---|---|---|
| Agent definition JSON | Prompt Engineer | Agent registry (ChromaDB + vault) |
| System prompt | Prompt Engineer | Inside agent definition |
| Few-shot examples | Prompt Engineer | Inside agent definition |
| Required tools (if new) | Tool Maker | Tool registry (ChromaDB + vault) |
| Initial performance record | Memory Manager | Inside agent definition |

---

## Registry Entry After Creation

```json
{
  "id": "blockchain-solidity-specialist",
  "version": "1.0.0",
  "status": "active",
  "created_at": "...",
  "approved_by": "human",
  "projects_used_in": 0,
  "evolution_log": [
    {
      "version": "1.0.0",
      "type": "initial_creation",
      "approved_by": "human",
      "summary": "Created for project-nft-marketplace-001"
    }
  ]
}
```

---

## Related Notes

- [[../02-Agents/BOOTSTRAP-CORE]]
- [[../02-Agents/DYNAMIC-AGENTS]]
- [[../05-Schemas/AGENT-DEFINITION]]
- [[EVOLUTION-CYCLE]]
- [[../06-Decisions/DESIGN-DECISIONS]] — DD-008
