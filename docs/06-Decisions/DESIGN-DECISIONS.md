# Design Decisions

tags: #decisions #rationale

---

## Decision Log

All significant design decisions made during the architecture phase, with rationale. This is the "why" record — future you (or Jules) should read this before changing anything.

---

### DD-001 — Self-assembling over pre-configured agents

**Decision:** Start with a small bootstrap core that creates agents dynamically, rather than pre-configuring a fixed team of 15+ agents.

**Rationale:** Pre-configured systems hit ceilings when a project needs something outside their configuration. A self-assembling system scales to any project type. The cost is slightly more complexity at startup; the benefit is unlimited flexibility going forward.

**Date:** 2024-03 | **Decided by:** Jeet + Claude

---

### DD-002 — LangGraph over CrewAI

**Decision:** Use LangGraph as the orchestration framework, with custom Python on top.

**Rationale:** CrewAI is faster to start but abstracts away the routing and state management that this system needs to control directly. LangGraph exposes DAG execution, conditional routing, and state as first-class primitives. At this system's complexity level, CrewAI would need to be fought rather than used.

**Date:** 2024-03 | **Decided by:** Claude (recommended), Jeet (approved)

---

### DD-003 — ChromaDB + Markdown Vault dual memory layer

**Decision:** Use ChromaDB for semantic search and a markdown vault (Obsidian-compatible) for human-readable structured notes. Both always in sync.

**Rationale:** ChromaDB gives the system fast semantic retrieval. The markdown vault gives the human (Jeet) full visibility into what the system knows, without needing to query a DB. Obsidian compatibility means the vault is immediately usable as a knowledge management tool.

**Date:** 2024-03 | **Decided by:** Claude (recommended), Jeet (approved). Jeet had the original insight about Obsidian-style memory.

---

### DD-004 — Option C hybrid approval model

**Decision:** Structural changes (new agent type, new tool category) require human approval. Refinements (prompt updates, tool patches, tool updates) require CEO approval only.

**Rationale:** Full human approval is too much friction for a system meant to be autonomous. Full autonomy is too risky for structural changes that affect the whole system. Option C keeps human control over architecture while letting the system polish itself.

**Date:** 2024-03 | **Decided by:** Jeet

---

### DD-005 — Manager layer between CEO and bootstrap core

**Decision:** Add Project Manager and Resource Manager agents as a Layer 2 between CEO and the bootstrap core.

**Rationale:** Without this layer, the CEO becomes a bottleneck when multiple projects run in parallel. The CEO should think at the goal/outcome level only. Project Managers own individual project execution. Resource Manager handles cross-project capacity. Clean separation of concerns.

**Date:** 2024-03 | **Decided by:** Jeet (original insight), Claude (elaborated)

---

### DD-006 — Team Leads scale with project size

**Decision:** Team Leads are only spawned for medium and large projects. Small projects have a flat structure (Project Manager → agents directly).

**Rationale:** Adding Team Leads to a small project creates overhead without benefit. The HR Agent determines scope from the Project Brief and structures accordingly.

**Scaling rules:**
- Small: 2-4 agents, no leads
- Medium: 2-3 leads, 2-3 agents each
- Large: 5+ leads, multiple agents each

**Date:** 2024-03 | **Decided by:** Jeet (original insight)

---

### DD-007 — Three-level evolution model

**Decision:** Evolution happens at three levels: per-project logging (automatic), end-of-project distillation (Memory Manager + CEO gate), and agent/tool definition updates (Prompt Engineer/Tool Maker + approval gate).

**Rationale:** A single-level evolution model either captures too little (only distilled, misses operational details) or produces too much noise (everything logged = nothing actionable). Three levels gives fidelity at runtime, clarity at close, and controlled change to the system.

**Date:** 2024-03 | **Decided by:** Claude (recommended), Jeet (approved)

---

### DD-008 — Unknown agent types: attempt autonomously with human notification

**Decision:** When a project needs a completely new agent type never before seen, the system attempts to build it autonomously via the bootstrap core, but flags for human approval before the agent is used.

**Rationale:** Blocking the whole project while waiting for human input slows the system unnecessarily. The Prompt Engineer can draft a new agent definition in parallel. The human approves the definition before it's used — no delay to the project preparation phase, but human stays in control of new agent types.

**Date:** 2024-03 | **Decided by:** Claude (recommended), Jeet (approved)

---

### DD-009 — Mid-project memory reporting threshold

**Decision:** Memory Manager produces interim reports when logged decisions exceed 50 within a project (and last report was >72 hours ago).

**Rationale:** For long-running projects, waiting until close to surface learnings means agents miss potentially relevant insights mid-project. 50 decisions is a reasonable signal that enough has happened to be worth a distillation pass.

**Threshold is configurable — start at 50, adjust based on experience.**

**Date:** 2024-03 | **Decided by:** Claude (recommended)

---

### DD-010 — Anthropic Claude API as LLM backend

**Decision:** All agent LLM calls use Claude (claude-sonnet-4-6) via the Anthropic API.

**Rationale:** This is Jeet's personal system. Consistency across all agent calls simplifies debugging. Claude handles structured output, tool use, and long context reliably. Can be revisited if specific agents benefit from specialist models.

**Date:** 2024-03 | **Decided by:** Claude (recommended), Jeet (approved)

---

### DD-011 — Provider-agnostic LLM abstraction layer

**Decision:** All LLM calls go through a single `call_llm()` function in `neuroforge/llm/client.py`. No agent calls any LLM SDK directly. The provider is determined entirely by `NEUROFORGE_PROVIDER` in config.

**Rationale:** Locking the system to one SDK makes provider switching a refactor. An abstraction layer makes it a config change. This future-proofs the system for local models (Ollama), alternative providers (Groq, Together), or cost optimisation (routing cheap tasks to smaller models) without touching any agent code.

**Supported providers at launch:**
- `anthropic` — Claude via Anthropic SDK (default)
- `openai` — GPT-4o and other OpenAI models
- `openai-compatible` — any OpenAI-spec endpoint via custom `NEUROFORGE_BASE_URL`

**Config fields introduced:**
- `NEUROFORGE_API_KEY` — single key field for all providers (replaces per-provider keys)
- `NEUROFORGE_PROVIDER` — selects the active provider (default: `anthropic`)
- `NEUROFORGE_BASE_URL` — only required for `openai-compatible`

**Date:** 2024-03 | **Decided by:** Jeet (raised), Claude (designed)

---

### DD-012 — Single NEUROFORGE_API_KEY over per-provider keys

**Decision:** Use a single `NEUROFORGE_API_KEY` environment variable for all LLM providers rather than keeping `ANTHROPIC_API_KEY` and adding separate OpenAI/other keys.

**Rationale:** A single key field makes provider switching completely seamless — you change `NEUROFORGE_PROVIDER`, update `NEUROFORGE_API_KEY` to the new provider's key, and nothing else changes. Per-provider keys require code changes every time a new provider is added. The slight loss of explicitness is worth the gain in simplicity.

**Date:** 2024-03 | **Decided by:** Jeet

---

## Related Notes

- [[OPEN-QUESTIONS]]
- [[../01-Architecture/SYSTEM-OVERVIEW]]
- [[../01-Architecture/TECH-STACK]]
