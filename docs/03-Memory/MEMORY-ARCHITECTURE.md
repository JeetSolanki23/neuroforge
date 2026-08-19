# Memory Architecture

tags: #memory #architecture #chromadb

---

## Overview

Memory is the connective tissue of the entire system. Without it, every project starts from zero. With it, every project makes the next one smarter. The memory system has two physical layers and five logical collections.

---

## Two Physical Layers

### Layer A — ChromaDB (vector store)
- Purpose: semantic search and retrieval
- Use: "find all past decisions related to JWT auth" → returns relevant chunks ranked by similarity
- Runs locally, persists to disk
- Accessed by agents via Memory Manager only (no direct access)

### Layer B — Markdown Vault (structured notes)
- Purpose: human-readable audit trail and reference
- Use: you open Obsidian and read exactly what the system decided and why
- Git-trackable
- Obsidian-compatible (backlinks, tags, graph view all work)

Every memory entry exists in both layers: raw content in ChromaDB for search, rendered markdown in the vault for reading.

---

## Five Logical Collections

### 1. Project Memory (operational)
**Scope:** One project, project duration only
**Content:** Everything that happened — every decision, task outcome, failure, retry, escalation
**Format:** Time-stamped event log
**Retention:** Archived at project close, raw logs kept for 90 days, then purged
**Stored in:** ChromaDB `project_memory` + `memory-vault/projects/{id}/decisions.md`

### 2. Learned Knowledge (permanent)
**Scope:** Cross-project, permanent
**Content:** Distilled insights that transfer — patterns, pitfalls, solutions
**Format:** Tagged knowledge entries (see [[../05-Schemas/MEMORY-ENTRY]])
**Retention:** Permanent, never auto-deleted
**Stored in:** ChromaDB `learned_knowledge` + `memory-vault/knowledge/{tag}/{id}.md`

### 3. Agent Registry (versioned)
**Scope:** All agent definitions ever created
**Content:** Full agent definition schemas, versioned
**Format:** See [[../05-Schemas/AGENT-DEFINITION]]
**Retention:** All versions kept permanently
**Stored in:** ChromaDB `agent_definitions` + `memory-vault/agents/{id}/v{version}.md`

### 4. Tool Registry (versioned)
**Scope:** All tools ever created
**Content:** Tool implementation, metadata, version history
**Format:** See [[../05-Schemas/TOOL-DEFINITION]]
**Retention:** All versions kept permanently (old versions marked deprecated)
**Stored in:** ChromaDB `tool_definitions` + `memory-vault/tools/{id}/v{version}.md`

### 5. Project Briefs (permanent)
**Scope:** All project briefs ever issued
**Content:** Structured project briefs
**Format:** See [[../05-Schemas/PROJECT-BRIEF]]
**Retention:** Permanent
**Stored in:** ChromaDB `project_briefs` + `memory-vault/projects/{id}/brief.md`

---

## Memory Flow Per Project

```
Project starts
    ↓
Memory Manager creates project memory space
Loads relevant past knowledge into agent context packets
    ↓
During project: operational events logged continuously
    ↓
Mid-project threshold crossed (50 decisions)?
    → Memory Manager produces interim report → CEO reviews
    ↓
Project closes
    ↓
Memory Manager distills operational → learned knowledge
Writes end-of-project summary to vault
Produces learnings report for CEO
    ↓
CEO reviews learnings
    → Review-worthy? → Surface to human
    → Not review-worthy? → Auto-archive
    ↓
Agent definitions updated if warranted (Prompt Engineer)
Tools updated if warranted (Tool Maker)
    ↓
Raw operational logs archived (purged after 90 days)
Learned knowledge permanent
```

---

## What Memory Manager Decides to Keep

Not everything gets promoted to learned knowledge. The Memory Manager uses these criteria:

**Keep if:**
- A decision was made that resolved a recurring ambiguity
- A failure occurred that wasn't in any past learned knowledge
- A pattern emerged that repeated 3+ times within the project
- A tech decision was made with clear reasoning (good or bad outcome)
- A new agent type or tool was created and performed well or poorly

**Discard if:**
- It's a routine task completion with no notable outcome
- It's a failure that's already well-represented in learned knowledge
- It's a trivial decision with no transferable value

---

## How Agents Query Memory

Agents never query ChromaDB directly. They receive context from the Memory Manager via their context packet. If an agent needs additional context during a task, it sends a retrieval request to the Memory Manager, which returns the top-k relevant entries.

```
Agent → "I need past decisions about PostgreSQL migrations"
    ↓
Memory Manager → semantic search in ChromaDB
    ↓
Returns top 5 relevant learned knowledge entries
    ↓
Agent receives and uses them
```

---

## Related Notes

- [[CHROMADB-SETUP]]
- [[MARKDOWN-VAULT]]
- [[../02-Agents/BOOTSTRAP-CORE]]
- [[../05-Schemas/MEMORY-ENTRY]]
