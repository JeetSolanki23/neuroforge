# Workflow: Evolution Cycle

tags: #workflow #evolution #agents #tools

---

## Overview

The system doesn't stay static. After every project, agents get smarter, tools get better, and the knowledge graph grows. This document describes exactly how that happens — the three levels of evolution and what triggers each.

---

## Three Levels of Evolution

### Level 1 — Per-Project Learning (automatic, during every project)

**What happens:**
Every decision, failure, resolution, and outcome is logged to operational memory by the Memory Manager throughout the project.

**When it fires:** Continuously, during all project phases

**What it produces:** Raw operational log (not yet useful to other projects)

**Who controls it:** Memory Manager (autonomous, no approval needed)

**Example:**
```
Event logged: "T6 — security-audit-specialist blocked T5 merge: 
JWT refresh token expiry not set. backend-django-specialist 
applied fix in 8 minutes. Root cause: not in default checklist."
```

---

### Level 2 — End-of-Project Distillation (automatic, after every project)

**What happens:**
Memory Manager converts operational logs into transferable learned knowledge entries. CEO reviews the distilled list and decides what reaches the human.

**When it fires:** At project close (and mid-project if decision volume > threshold)

**What it produces:**
- Learned knowledge entries in ChromaDB and vault
- Agent performance notes
- Proposed agent definition changes (to CEO for approval)
- Human-surfaced items (if CEO decides)

**Who controls it:**
- Memory Manager: distillation (autonomous)
- CEO: review and approval gate
- Human: sees only what CEO surfaces

**Approval matrix:**
| Change type | Approved by |
|---|---|
| New learned knowledge entry | CEO (autonomous) |
| Agent prompt refinement | CEO approves → Prompt Engineer executes |
| Agent constraint change | Human approves |
| Agent new capability added | Human approves |
| Tool patch (bug fix) | CEO approves → Tool Maker executes |
| Tool new version (new feature) | CEO approves → Tool Maker executes |
| Tool new type (new category) | Human approves |

**Example distillation:**
```
Operational log entry (raw):
  "JWT refresh expiry bug, fixed in 8min, caught by security agent"

Distilled learned knowledge:
  id: LK-2024-031
  title: "JWT refresh tokens require explicit expiry — easy to miss"
  domain: backend, auth
  applies_to: [backend-django-specialist, backend-fastapi-specialist, backend-node-specialist]
  lesson: "Refresh tokens do not inherit access token expiry settings. 
           Must be set explicitly. Add to auth checklist."
  evidence: project-todo-api-01
  confidence: medium (one occurrence)
```

---

### Level 3 — Agent Definition Evolution (on approval, after distillation)

**What happens:**
Based on distilled learnings, the Prompt Engineer proposes changes to existing agent definitions. These are versioned and saved to the agent registry.

**When it fires:** After CEO approves a proposed change from Level 2

**What it produces:**
- New version of agent definition (v1.0.0 → v1.1.0)
- Evolution log entry on the definition
- Updated ChromaDB and vault entry

**Example:**
```
Change proposed: "Add JWT refresh expiry check to backend-django-specialist checklist"

Before (v1.0.0 system prompt excerpt):
  "When implementing JWT authentication, use djangorestframework-simplejwt..."

After (v1.1.0 system prompt excerpt):  
  "When implementing JWT authentication, use djangorestframework-simplejwt...
   CHECKLIST: Always set REFRESH_TOKEN_LIFETIME explicitly in SIMPLE_JWT settings.
   Refresh tokens do not inherit ACCESS_TOKEN_LIFETIME. (LK-2024-031)"

Evolution log entry:
  v1.1.0 | auto-refinement | 2024-xx-xx | "Added JWT refresh expiry checklist item (LK-2024-031)"
```

---

## Tool Evolution

Tools follow the same three-level pattern but with their own approval rules:

```
Bug found in tool during project
    ↓
Tool Maker proposes patch
    ↓
CEO approves → patch applied → Tool v1.0.1 saved

New capability needed that extends existing tool
    ↓  
Tool Maker proposes new version
    ↓
CEO approves → new version → Tool v1.1.0 saved

Genuinely new tool category needed
    ↓
CEO flags to human → Human approves
    ↓
Tool Maker builds → Tool v1.0.0 saved → Human notified
```

All old versions are kept. Projects can pin to a specific tool version if needed.

---

## How the System Gets Smarter Over Time

After 10 projects, your system has:
- Agent definitions refined with real-world checklists from actual bugs
- Learned knowledge entries covering common pitfalls in your stack
- Tool versions that handle edge cases discovered in past work
- Accurate time estimates derived from actual project duration data
- A knowledge graph that gets queried to give every new agent a head start

After 50 projects, it has essentially built up the equivalent of a senior developer's intuition — not from training data, but from your specific projects, your specific stack preferences, and your specific failure patterns.

---

## Mid-Project Evolution Trigger

For long-running projects, waiting until close is too long. The trigger:

```
IF logged_decisions_this_project > 50
AND last_interim_report_was > 72_hours_ago
THEN Memory Manager → produce interim distillation → report to CEO
```

Same approval flow as end-of-project. Same human surfacing logic.

---

## Related Notes

- [[../03-Memory/MEMORY-ARCHITECTURE]]
- [[../02-Agents/BOOTSTRAP-CORE]]
- [[../05-Schemas/AGENT-DEFINITION]]
- [[AGENT-CREATION]]
