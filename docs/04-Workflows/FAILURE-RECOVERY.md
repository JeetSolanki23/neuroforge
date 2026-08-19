# Workflow: Failure Recovery

tags: #workflow #failure #recovery

---

## Philosophy

Failure is not binary. A task failing once is not the same as a task being impossible. The recovery model is **layered and graduated** — each layer escalates only when the previous one is exhausted.

---

## The Four Layers

### Layer 1 — Retry (same agent, same task)

**Trigger:** Task returns failure or timeout
**Action:** Retry up to 3 times with the same agent
**Why it works:** LLM outputs are non-deterministic. A second attempt often succeeds where the first failed — especially for tasks that involve code generation or tool calls.
**Max attempts:** 3
**Escalates to:** Layer 2 if all 3 fail

---

### Layer 2 — Reassign (different agent instance, same type)

**Trigger:** 3 retries exhausted
**Action:** Resource Manager provides a fresh instance of the same agent type. Task dispatched with a note: "Previous attempt failed. Approach differently."
**Why it works:** A different instance starts with no priors from the failed attempts and may find a different path.
**Escalates to:** Layer 3 if fresh instance also fails

---

### Layer 3 — Re-plan (decompose task differently)

**Trigger:** Fresh instance also fails
**Action:** Project Manager re-examines the task. Either:
  - Breaks it into smaller sub-tasks
  - Reorders dependencies (maybe this task needs a blocker resolved first)
  - Injects additional context from memory
**Why it works:** The task may have been too large, too ambiguous, or missing context.
**Escalates to:** Layer 4 if re-planning doesn't resolve it

---

### Layer 4 — Escalate to CEO (human-level decision)

**Trigger:** Re-planning exhausts options
**Action:** Project Manager escalates to CEO with:
  - What the task was
  - What was attempted (all 3 layers)
  - What the blocker appears to be
  - CEO's options: intervene, descope, or escalate to human

**CEO can:**
- Resolve autonomously (if the blocker is a context gap CEO can fill)
- Surface to human (if the blocker requires a decision only the human can make)
- Cancel/descope the task (if it's non-critical and blocking progress)

---

## Specific Failure Scenarios

### Agent produces wrong output format
```
Layer 1: Retry with format reminder injected into prompt
Layer 2: Fresh instance
Layer 3: Simplify output requirements, add example
```

### Agent is blocked by missing dependency
```
Do NOT retry — this is a DAG issue, not an agent issue
Project Manager: identify which upstream task is missing
Re-order DAG or escalate upstream task
```

### Tool call fails (tool error or API error)
```
Layer 1: Retry tool call (transient errors)
Layer 2: Tool Maker investigates and patches (if tool bug)
Layer 3: Alternative tool if available
Layer 4: CEO — human may need to resolve if tool is broken and no alternative
```

### Agent hallucinates (produces plausible but wrong output)
```
This is caught by: Code Review agent, QA agent, or downstream agent finding inconsistency
Action: Flag to Project Manager → retry with explicit grounding instructions
```

### Two agents conflict (e.g. same file edited differently)
```
Project Manager: arbitrate using Project Brief as authority
If Brief doesn't resolve it: Team Lead decides (within domain)
If cross-domain: Project Manager decides
If still unresolved: CEO decides
```

---

## What Gets Logged

Every failure and recovery action is logged to operational memory with:
- Agent ID and task ID
- Layer reached before resolution
- Root cause (if identifiable)
- Resolution applied

This feeds the evolution cycle — recurring failure patterns trigger agent definition improvements.

---

## Related Notes

- [[../02-Agents/PROJECT-MANAGER]]
- [[../02-Agents/CEO-ORCHESTRATOR]]
- [[GOAL-TO-SOFTWARE]]
- [[EVOLUTION-CYCLE]]
