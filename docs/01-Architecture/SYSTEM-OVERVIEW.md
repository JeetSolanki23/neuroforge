# System Overview

tags: #architecture #overview

---

## What This System Is

NeuroForge is a self-assembling, self-evolving AI software company. It is not a fixed team of pre-configured agents. It is a small set of **founding agents** capable of creating, configuring, and coordinating any team composition required by a given goal.

The human (you) interacts only at the goal level and at structural decision points. Everything between goal and shipped software is autonomous.

---

## The Five Layers

```
┌─────────────────────────────────────────────────┐
│  LAYER 1 — ORCHESTRATION                        │
│  CEO / Orchestrator                             │
│  Receives goals, issues project briefs,         │
│  approves teams, reviews outcomes               │
├─────────────────────────────────────────────────┤
│  LAYER 2 — MANAGEMENT                           │
│  Project Manager · Resource Manager             │
│  Runs individual projects, tracks agent load    │
│  across all active work                         │
├─────────────────────────────────────────────────┤
│  LAYER 3 — BOOTSTRAP CORE                       │
│  HR · Prompt Engineer · Tool Maker ·            │
│  Memory Manager                                 │
│  Always running. Creates everything else.       │
├─────────────────────────────────────────────────┤
│  LAYER 4 — DYNAMIC AGENTS                       │
│  Team Leads + Specialist agents                 │
│  Spawned per project. Definitions saved.        │
├─────────────────────────────────────────────────┤
│  LAYER 5 — SHARED MEMORY                        │
│  ChromaDB + Markdown Vault                      │
│  Project memory · Learned knowledge ·           │
│  Agent registry · Tool registry                 │
└─────────────────────────────────────────────────┘
```

---

## Design Philosophy

### Why not pre-configure everything?
A fixed team of 15 agents means you always have 15 agents whether the project needs 3 or 30. Pre-configured systems hit walls when they encounter something outside their configuration. This system creates what it needs, when it needs it.

### Why a bootstrap core instead of no fixed agents?
Pure dynamic systems have no starting point — you need something to create the creators. The bootstrap core is the minimum viable founding team: agents that can build agents, write their instructions, equip them with tools, and remember what worked.

### Why shared memory as a first-class layer?
Without shared memory, agents work in silos and contradict each other. The memory layer is the connective tissue that allows an architect's decision to automatically inform a backend agent's behavior without explicit message passing.

### Why does project structure scale with size?
Small projects get a flat team (Project Manager → agents directly). Large projects get Team Leads per domain. The system assesses project scope from the brief and structures accordingly. Overhead is always proportional to need.

---

## What the Human Controls

Under **Option C (Hybrid approval)**:

| Action | Who approves |
|---|---|
| New agent type created | Human (you) |
| New tool created | Human (you) |
| Agent prompt refinement | Autonomous (CEO gate) |
| Tool version update | Autonomous (CEO gate) |
| Team composition for a project | Autonomous (CEO gate) |
| Memory surfaced as review-worthy | Human (you) — CEO decides whether to ask |
| Tech stack selection | CEO approves, surfaces to human if novel |

---

## Related Notes

- [[AGENT-HIERARCHY]] — full hierarchy diagram and role descriptions
- [[TECH-STACK]] — technology decisions
- [[../04-Workflows/GOAL-TO-SOFTWARE]] — end-to-end flow
