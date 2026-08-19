# Bootstrap Core Agents

tags: #agent #bootstrap #permanent

---

## Overview

The bootstrap core is the founding team — four agents that always exist and cannot be deleted. Their collective job is to create, configure, equip, and remember everything else. No project can start without them. No new agent or tool exists without going through them.

---

## 1. HR Agent

### Role
Team composer. When the CEO says "I need a team for a Django REST API project with a React frontend," the HR Agent decides exactly which agent types to request, in what configuration, at what scale.

### Responsibilities
- Read the Project Brief
- Determine required agent types and count based on scope
- Check Resource Manager for agent availability
- Request Prompt Engineer to configure each agent
- Propose final team structure to CEO for approval
- Spawn agents once approved
- Assign Team Leads for medium/large projects

### Inputs
- Project Brief (from CEO via Project Manager)
- Agent registry (from Memory layer)
- Current resource availability (from Resource Manager)

### Outputs
- Proposed team structure (to CEO for approval)
- Agent spawn requests (to Prompt Engineer)

### Scaling logic
```
scope = SMALL  → 2-4 specialists, no team leads, flat structure
scope = MEDIUM → 2-3 team leads, 2-3 specialists each
scope = LARGE  → full domain team leads, multiple specialists each
```

---

## 2. Prompt Engineer Agent

### Role
Writer of agent minds. Every agent that gets created receives its identity, behavior rules, capabilities, and constraints from a system prompt written by this agent. It also maintains and evolves existing prompts over time.

### Responsibilities
- Write system prompts for newly requested agent types
- Customise existing agent definitions for project-specific context
- Propose prompt refinements based on post-project learnings (CEO approves)
- Maintain prompt versioning in agent definitions
- Ensure all prompts include: role, constraints, escalation rules, output format

### Inputs
- Agent type requested (from HR Agent)
- Project context (from Project Brief)
- Past performance data for this agent type (from Memory layer)
- Proposed refinements (from Memory Manager post-project)

### Outputs
- Completed agent definition (to Agent Registry)
- Refined agent definition (to Agent Registry, pending CEO approval)

### Prompt structure it always produces
```
1. Identity — who this agent is and its single responsibility
2. Inputs — what it receives and in what format
3. Outputs — what it must produce and in what format
4. Constraints — what it must never do
5. Escalation rules — when to escalate and to whom
6. Few-shot examples — 2-3 examples of correct behavior
```

---

## 3. Tool Maker Agent

### Role
Builder of agent capabilities. Agents can only do what their tools allow. When an agent needs to call an API, read a file, run tests, or interact with a service, the Tool Maker writes that tool as a versioned, callable Python function.

### Responsibilities
- Build new tools when agents encounter missing capabilities
- Version and register all tools in the Tool Registry
- Patch tools when bugs are found (CEO approves, no human needed)
- Build new tool types when a genuinely new capability is needed (Human approves)
- Maintain tool documentation alongside each version

### Inputs
- Tool request (from any agent via Project Manager escalation)
- Existing tool registry (from Memory layer)

### Outputs
- Tool implementation (Python function + metadata)
- Tool definition entry (to Tool Registry)

### Tool categories it builds
```
file_tools      → read, write, create files and directories
api_tools       → call external APIs, handle auth and rate limits
code_tools      → run code, capture output, handle errors
test_tools      → run test suites, parse results, report failures
search_tools    → semantic search in memory, web search
git_tools       → commit, branch, merge, PR creation
system_tools    → shell commands, environment management
```

### New tool type policy (Option C)
- Tool **patch** (fix existing) → Tool Maker creates → CEO approves automatically
- Tool **update** (new version, same capability) → Tool Maker creates → CEO approves
- Tool **new type** (genuinely new capability category) → Tool Maker proposes → **Human approves**

---

## 4. Memory Manager Agent

### Role
The keeper of everything the system has ever learned. It owns the knowledge graph, decides what is worth remembering, converts raw project logs into transferable insights, and surfaces information to agents that need it.

### Responsibilities
- Maintain operational memory during a project (detailed log of all events)
- At project close: distill operational memory into learned knowledge
- Report distilled learnings to CEO at project end
- Report mid-project if logged decision volume crosses threshold
- Serve relevant context to agents on request (semantic search via ChromaDB)
- Tag and index all memory entries for retrieval

### Two memory tiers it maintains

**Operational memory** (project duration only)
- Every decision made and by whom
- Every task outcome (success / failure / retry)
- Every tool call result
- Every escalation and its resolution
- Raw, detailed, time-stamped

**Learned memory** (permanent, cross-project)
- Distilled insights that transfer to future projects
- Patterns of failure and how they were resolved
- Tech decisions and their outcomes
- Agent performance notes
- Human-readable, tagged, searchable

### Reporting to CEO

**End of project:**
1. Produces a learnings report (distilled, not raw logs)
2. Flags any items it considers review-worthy for the human
3. CEO decides whether to surface to human

**Mid-project trigger:**
- Fires when `logged_decisions > threshold` (default: 50 decisions)
- Same format and process as end-of-project report
- Does not interrupt active agent work — async report

### Memory entry format
See [[../05-Schemas/MEMORY-ENTRY]]

---

## Related Notes

- [[../01-Architecture/AGENT-HIERARCHY]]
- [[../03-Memory/MEMORY-ARCHITECTURE]]
- [[../05-Schemas/AGENT-DEFINITION]]
- [[../05-Schemas/TOOL-DEFINITION]]
- [[DYNAMIC-AGENTS]]
