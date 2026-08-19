# NeuroForge

A self-assembling, self-evolving AI software company. Give it a goal — it forms the right team, builds the software, and gets smarter with every project.

---

## What It Does

NeuroForge is a multi-agent system that acts as your personal AI development team. Instead of writing code yourself, you describe what you want built. The system assembles the right team of AI agents, executes the project autonomously, and learns from every project to improve future work.

## How It Works

```
You → "Build me a REST API with auth and PostgreSQL"
         ↓
CEO Agent parses goal → produces Project Brief
         ↓
HR Agent composes the right team for this project
         ↓
Agents build in parallel, supervised by a Project Manager
         ↓
QA + Security agents review before delivery
         ↓
Memory Manager distills learnings → system improves
         ↓
You receive working software
```

## Architecture

Five layers:

| Layer | Agents | Role |
|---|---|---|
| Orchestration | CEO | Goal intake, team approval, outcome review |
| Management | Project Manager, Resource Manager | Per-project execution, cross-project capacity |
| Bootstrap Core | HR, Prompt Engineer, Tool Maker, Memory Manager | Creates and evolves all other agents |
| Dynamic | Team Leads + Specialists | Actually builds the software |
| Memory | ChromaDB + Markdown Vault | Shared knowledge across all projects |

Full documentation in [`docs/`](./docs/00-Index/HOME.md).

## Tech Stack

- **Orchestration:** LangGraph
- **LLM:** Anthropic Claude (claude-sonnet-4-6)
- **Vector DB:** ChromaDB (local)
- **Memory vault:** Obsidian-compatible markdown
- **Language:** Python 3.11+

## Project Structure

```
neuroforge/
├── docs/               # Architecture documentation (Obsidian vault)
├── neuroforge/         # Python package
│   ├── agents/         # Agent implementations
│   ├── memory/         # ChromaDB + vault interface
│   ├── tools/          # Tool implementations
│   ├── workflows/      # LangGraph workflow definitions
│   └── schemas/        # Pydantic schemas
├── memory-vault/       # Runtime memory (gitignored contents)
└── tests/
```

## Setup

```bash
# Clone
git clone https://github.com/yourusername/neuroforge.git
cd neuroforge

# Install
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Configure
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# Run
python -m neuroforge
```

## Status

Currently in architecture and initial implementation phase. See [`docs/00-Index/HOME.md`](./docs/00-Index/HOME.md) for full design documentation and implementation status.

---

*Built with Claude (Anthropic) as architecture supervisor.*
