# NeuroForge — AI Software Company

> A self-assembling, self-evolving multi-agent system that builds software autonomously. You give it a goal. It forms the right team, builds the software, learns from every project, and gets smarter over time.

---

## Vault Map

| Section | Description |
|---|---|
| [[01-Architecture/SYSTEM-OVERVIEW]] | Full system architecture, layers, and design philosophy |
| [[01-Architecture/AGENT-HIERARCHY]] | Complete agent hierarchy with roles and relationships |
| [[01-Architecture/TECH-STACK]] | Technology decisions and rationale |
| [[02-Agents/CEO-ORCHESTRATOR]] | CEO / Orchestrator agent — detailed spec |
| [[02-Agents/PROJECT-MANAGER]] | Project Manager agent — detailed spec |
| [[02-Agents/RESOURCE-MANAGER]] | Resource Manager agent — detailed spec |
| [[02-Agents/BOOTSTRAP-CORE]] | All four bootstrap core agents |
| [[02-Agents/TEAM-LEAD]] | Team Lead agent — detailed spec |
| [[02-Agents/DYNAMIC-AGENTS]] | How dynamic agents are spawned and configured |
| [[03-Memory/MEMORY-ARCHITECTURE]] | Full memory system design |
| [[03-Memory/CHROMADB-SETUP]] | ChromaDB configuration and schema |
| [[03-Memory/MARKDOWN-VAULT]] | Structured markdown vault conventions |
| [[04-Workflows/GOAL-TO-SOFTWARE]] | End-to-end flow from goal input to shipped software |
| [[04-Workflows/AGENT-CREATION]] | How new agent types get created autonomously |
| [[04-Workflows/EVOLUTION-CYCLE]] | How agents and tools evolve between projects |
| [[04-Workflows/FAILURE-RECOVERY]] | Layered failure recovery model |
| [[05-Schemas/AGENT-DEFINITION]] | Agent definition schema (versioned) |
| [[05-Schemas/PROJECT-BRIEF]] | Project brief schema |
| [[05-Schemas/MEMORY-ENTRY]] | Memory entry schema |
| [[05-Schemas/TOOL-DEFINITION]] | Tool definition schema |
| [[06-Decisions/DESIGN-DECISIONS]] | All key design decisions and rationale |
| [[06-Decisions/OPEN-QUESTIONS]] | Unresolved questions and future considerations |

---

## Core Principles

1. **Self-assembling** — the system forms its own teams based on what the goal needs, not what was pre-configured
2. **Self-evolving** — every project makes the system smarter; agents improve their own definitions over time
3. **Hierarchical control** — clear chain of command with appropriate decision authority at each level
4. **Memory-first** — shared memory is the connective tissue; no agent works in isolation
5. **Human in the loop (lightly)** — structural changes require approval; refinements happen autonomously (Option C)
6. **Proportional structure** — team complexity scales with project size; small projects don't get unnecessary overhead

---

## Status

- [x] System architecture designed
- [x] Agent hierarchy defined
- [x] Memory architecture designed
- [x] Schemas defined
- [x] Workflows documented
- [ ] Tech stack implementation (Jules — pending)
- [ ] Bootstrap core agent implementation
- [ ] Memory layer implementation
- [ ] CEO orchestrator implementation
- [ ] End-to-end testing

---

*Created: {{date}}*
*Last updated: {{date}}*
