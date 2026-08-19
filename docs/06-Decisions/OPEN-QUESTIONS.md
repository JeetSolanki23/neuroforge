# Open Questions

tags: #decisions #open #future

---

## Active Open Questions

These are unresolved design questions. They don't block implementation of Phase 1 but should be decided before they become relevant.

---

### OQ-001 — Agent sandboxing for code execution

**Question:** When a specialist agent runs code (via `run_python` or `run_tests`), should it run in a sandboxed environment (Docker container, subprocess with limits) or directly on the host machine?

**Why it matters:** Agents writing and running code could accidentally damage the file system, consume excessive resources, or run malicious code if a prompt injection occurred.

**Options:**
- A: Run directly on host (simple, fast, risky)
- B: Run in a Docker container per agent (safe, adds setup complexity)
- C: Run in a restricted subprocess with resource limits (middle ground)

**Recommendation:** Option C for Phase 1, Option B for production.

**Status:** Unresolved — decide before first code-execution agent is implemented.

---

### OQ-002 — Multi-project parallelism limit

**Question:** How many projects should run in parallel at maximum?

**Why it matters:** Each active project spawns multiple agent instances, each making API calls. Costs and rate limits scale with parallelism.

**Options:**
- Hard cap (e.g. max 3 concurrent projects)
- Soft cap with Resource Manager queue
- No cap, let Resource Manager manage dynamically

**Recommendation:** Start with soft cap of 3. Resource Manager queues beyond that.

**Status:** Unresolved — not needed until you have multiple concurrent projects.

---

### OQ-003 — Agent instance reuse vs fresh instances

**Question:** When the same agent type is needed for a new project, should it reuse the same instance (with its conversation history) or start fresh from the definition?

**Why it matters:** Reuse could cause context bleed between projects. Fresh instances are clean but lose any in-conversation learning.

**Recommendation:** Always start fresh from the definition. All learning goes through the evolution cycle, not instance memory. Conversation history within a project is fine; cross-project history is not.

**Status:** Resolved in principle (fresh instances), not yet implemented.

---

### OQ-004 — Human notification interface

**Question:** How does the system surface things to Jeet? Options:
- CLI output in terminal
- A web dashboard
- Markdown file written to vault (he reads it in Obsidian)
- Slack/Discord webhook

**Why it matters:** The system needs a reliable way to ask for approval on new agent types, surface memory reviews, and report project outcomes.

**Recommendation:** Phase 1 — CLI + markdown file in vault. Phase 2 — simple web dashboard.

**Status:** Unresolved — needed for first implementation.

---

### OQ-005 — Git strategy for agent-written code

**Question:** How does agent-written code get committed and reviewed?

**Options:**
- Agents commit directly to feature branches, Jeet reviews PRs
- Agents write to working directory, Jeet decides when to commit
- Code Review agent creates a PR, Jeet merges

**Recommendation:** Code Review agent creates a PR on a feature branch → Jeet reviews and merges. This keeps Jeet in control of what enters the codebase without blocking agent execution.

**Status:** Unresolved.

---

### OQ-006 — Memory vault location

**Question:** Where does the markdown vault live?

**Options:**
- Inside the NeuroForge project repo (memory tracked with code)
- Separate repo (memory versioned independently)
- Obsidian vault synced via iCloud/Obsidian Sync (accessible on phone)

**Recommendation:** Separate repo, symlinked into Obsidian vault. This way you can open it in Obsidian while it's also Git-tracked.

**Status:** Unresolved — decide before memory layer is implemented.

---

## Resolved Questions (moved here from active)

| OQ | Question | Resolution | DD ref |
|---|---|---|---|
| Framework choice | LangGraph vs CrewAI | LangGraph | DD-002 |
| Memory stack | What DB + what format | ChromaDB + Markdown | DD-003 |
| Approval model | How much human control | Option C hybrid | DD-004 |
| New agent type policy | Who decides | Human approves, system drafts | DD-008 |
| Evolution trigger | When to report mid-project | 50 decisions + 72hr gap | DD-009 |

---

## Future Scope (not in Phase 1)

These are ideas worth capturing but explicitly out of scope until the core system is working:

- **Agent marketplace** — publishing and sharing agent definitions with others
- **Multi-user support** — more than one person using the same NeuroForge instance
- **Cloud deployment** — moving from local to cloud-hosted agents
- **Specialized model routing** — using different LLMs for different agent types
- **Visual project dashboard** — web UI for monitoring active projects
- **Agent capability ratings** — public leaderboard of agent performance across users

---

## Related Notes

- [[DESIGN-DECISIONS]]
- [[../01-Architecture/SYSTEM-OVERVIEW]]
