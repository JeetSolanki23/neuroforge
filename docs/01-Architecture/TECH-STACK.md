# Tech Stack

tags: #architecture #tech-stack #decisions

---

## Orchestration Framework

**Chosen: LangGraph + custom Python**

| Option | Pros | Cons | Decision |
|---|---|---|---|
| LangGraph | Full control, explicit state machine, DAG-native, production-grade | More setup than CrewAI | ✅ Chosen |
| CrewAI | Fast to start, simple API | Abstracts too much, hits walls with complex routing | ❌ Rejected |
| Custom Python only | Maximum flexibility | Too much reinvention of solved problems | ❌ Rejected |

**Rationale:** This system needs custom routing logic, dynamic agent creation, and complex DAG execution. LangGraph exposes these as first-class primitives. CrewAI would need to be worked around rather than with at this complexity level.

---

## Memory Stack

**Chosen: ChromaDB (vector) + Markdown Vault (structured)**

### ChromaDB
- Runs fully local — no server, no cloud dependency
- Zero configuration to start
- Stores embeddings for semantic search across past decisions
- Python-native client
- Human-inspectable via CLI

**Collections structure:**
```
chroma/
├── agent_definitions     # all agent schemas, versioned
├── tool_definitions      # all tool schemas, versioned  
├── project_memory        # per-project operational logs
├── learned_knowledge     # cross-project distilled insights
└── project_briefs        # all project briefs, searchable
```

### Markdown Vault (Obsidian-compatible)
- Human-readable at all times
- Git-trackable
- Obsidian-compatible for your review
- Structured frontmatter for metadata

**Vault structure:**
```
memory-vault/
├── projects/
│   └── {project-id}/
│       ├── brief.md
│       ├── decisions.md
│       ├── outcomes.md
│       └── learned.md
├── agents/
│   └── {agent-id}/
│       └── v{version}.md
├── tools/
│   └── {tool-id}/
│       └── v{version}.md
└── knowledge/
    └── {tag}/
        └── {insight-id}.md
```

---

## Runtime Environment

**Local machine (Phase 1)**

- Python 3.11+
- All processes run locally
- No cloud dependencies in Phase 1
- ChromaDB persists to local disk
- Markdown vault synced via Obsidian

**Future (Phase 2+):**
- API server for multi-project parallelism
- Optional cloud ChromaDB for persistence across machines
- Agent sandboxing for code execution safety

---

## LLM Backend

**Provider-agnostic via abstraction layer**

All agent LLM calls go through a single `call_llm()` interface in `neuroforge/llm/client.py` — never directly to any SDK. Swapping providers is a config change, not a code change.

Supported providers (set via `NEUROFORGE_PROVIDER` in `.env`):

| Provider value | SDK used | Use case |
|---|---|---|
| `anthropic` | anthropic | Default — Claude models |
| `openai` | openai | GPT-4o and other OpenAI models |
| `openai-compatible` | openai (custom base_url) | Ollama, Groq, Together, any local model |

**Default config:**
```
NEUROFORGE_PROVIDER=anthropic
NEUROFORGE_MODEL=claude-sonnet-4-6
NEUROFORGE_API_KEY=your_key_here
NEUROFORGE_BASE_URL=        ← only needed for openai-compatible
```

**To switch to a local Ollama model — only .env changes:**
```
NEUROFORGE_PROVIDER=openai-compatible
NEUROFORGE_MODEL=llama3.1:70b
NEUROFORGE_BASE_URL=http://localhost:11434/v1
```

- Each agent call is stateless — full context injected per call
- Conversation history managed by the orchestration layer
- Structured output via XML tags + JSON schema enforcement (provider-independent)

---

## Language & Key Libraries

```
Language:        Python 3.11+
Orchestration:   LangGraph
LLM (default):   anthropic SDK → Claude
LLM (alt):       openai SDK → GPT-4o or any OpenAI-compatible endpoint
LLM Abstraction: neuroforge/llm/client.py — single call_llm() interface
Vector DB:       chromadb (local, no server)
Embeddings:      sentence-transformers model: all-MiniLM-L6-v2 (local, no API cost)
Config:          pydantic-settings (BaseSettings, loads from .env)
Validation:      pydantic v2
Storage:         pathlib + json (agent/tool definitions)
Logging:         structlog
CLI:             typer — `neuroforge` command available from day one
Testing:         pytest + pytest-cov
```

---

## What Jules Will Set Up

**Phase 1 — Foundation (current)**
- [ ] `pyproject.toml` — dependencies, CLI entry point (`neuroforge` command)
- [ ] `neuroforge/config.py` — Pydantic BaseSettings, all env vars
- [ ] `neuroforge/logger.py` — structlog setup, `get_logger(name)`
- [ ] `neuroforge/llm/client.py` — provider-agnostic `call_llm()` interface
- [ ] `neuroforge/memory/chroma.py` — ChromaDB init, 5 collections
- [ ] `neuroforge/schemas/base.py` — lean Pydantic models for core schemas
- [ ] `tests/` — config, chroma, llm unit tests (no real API calls)

**Phase 2 — Bootstrap Core**
- [ ] `neuroforge/agents/base.py` — base agent class all agents inherit from
- [ ] `neuroforge/agents/ceo.py` — CEO orchestrator
- [ ] `neuroforge/agents/hr.py` — HR agent
- [ ] `neuroforge/agents/prompt_engineer.py`
- [ ] `neuroforge/agents/tool_maker.py`
- [ ] `neuroforge/agents/memory_manager.py`

**Phase 3 — Management Layer**
- [ ] `neuroforge/agents/project_manager.py`
- [ ] `neuroforge/agents/resource_manager.py`
- [ ] `neuroforge/workflows/project_dag.py` — LangGraph DAG definition

**Phase 4 — Dynamic Agents + Full System**
- [ ] `neuroforge/agents/team_lead.py`
- [ ] `neuroforge/agents/dynamic.py` — dynamic agent spawning
- [ ] `neuroforge/workflows/orchestrator.py` — full CEO LangGraph
- [ ] End-to-end integration tests

---

## Related Notes

- [[SYSTEM-OVERVIEW]]
- [[../03-Memory/CHROMADB-SETUP]]
- [[../03-Memory/MARKDOWN-VAULT]]
