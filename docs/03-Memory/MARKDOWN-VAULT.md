# Markdown Vault Conventions

tags: #memory #vault #obsidian

---

## Purpose

The markdown vault is the human-readable layer of the memory system. Everything in ChromaDB also has a markdown counterpart here. You can open this in Obsidian and read the full history of every decision, agent, and project.

---

## Directory Structure

```
memory-vault/
├── projects/
│   └── {project-id}/
│       ├── brief.md          ← Project Brief (human readable)
│       ├── decisions.md      ← Key decisions made during project
│       ├── outcomes.md       ← What was built, test results, QA outcome
│       └── learned.md        ← Distilled learnings from this project
├── agents/
│   └── {agent-id}/
│       ├── v1.0.0.md         ← Agent definition at each version
│       ├── v1.1.0.md
│       └── current.md        ← Symlink or copy of latest version
├── tools/
│   └── {tool-id}/
│       ├── v1.0.0.md
│       └── current.md
└── knowledge/
    ├── backend/
    ├── frontend/
    ├── auth/
    ├── security/
    ├── devops/
    └── general/
```

---

## Frontmatter Convention

Every file in the vault uses YAML frontmatter for Obsidian compatibility:

```yaml
---
id: LK-2024-031
type: learned_knowledge
domain: [backend, auth, security]
confidence: medium
created: 2024-02-08
approved_by: ceo-agent
surfaced_to_human: true
tags: [jwt, auth, django, refresh-token]
---
```

---

## File Naming Convention

```
projects/    → {YYYY-MM}-{short-name}/
agents/      → {agent-id}/v{major}.{minor}.{patch}.md
tools/       → {tool-id}/v{major}.{minor}.{patch}.md
knowledge/   → {domain}/{LK-YYYY-NNN}-{short-title}.md
```

---

## Obsidian Setup

1. Open Obsidian
2. "Open folder as vault" → select `memory-vault/`
3. Install plugins (optional but recommended):
   - **Dataview** — query your agents and learnings like a database
   - **Graph view** — visualise connections between agents, projects, and knowledge
   - **Templater** — auto-fill frontmatter on new files

### Useful Dataview queries for Obsidian:

```dataview
TABLE confidence, domain, created
FROM "knowledge/"
WHERE surfaced_to_human = true
SORT created DESC
```

```dataview
TABLE version, projects_used_in, success_rate
FROM "agents/"
WHERE contains(file.name, "current")
SORT success_rate DESC
```

---

## Write Rules (for Memory Manager agent)

1. Every entry written to ChromaDB **must** also be written to the vault
2. Vault files are append-only for logs (decisions.md) — never overwrite history
3. Frontmatter must always be present and valid YAML
4. Internal links use Obsidian `[[double bracket]]` syntax
5. Tags must match the ChromaDB metadata tags exactly

---

## Related Notes

- [[MEMORY-ARCHITECTURE]]
- [[CHROMADB-SETUP]]
- [[../01-Architecture/TECH-STACK]]
