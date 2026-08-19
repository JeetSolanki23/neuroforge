# Agent Hierarchy

tags: #architecture #agents #hierarchy

---

## Full Hierarchy

```
CEO / Orchestrator
│
├── Project Manager (one per active project)
│   │
│   ├── [Small project] → Agents directly
│   │
│   └── [Medium/Large project]
│       ├── Team Lead — Design
│       │   ├── UI/UX Agent
│       │   └── Design System Agent
│       ├── Team Lead — Frontend
│       │   ├── React/Vue Agent
│       │   └── State Management Agent
│       ├── Team Lead — Backend
│       │   ├── API Agent
│       │   ├── Database Agent
│       │   └── Auth Agent
│       ├── Team Lead — DevOps
│       │   ├── CI/CD Agent
│       │   └── Infrastructure Agent
│       └── Team Lead — QA
│           ├── Test Writer Agent
│           └── Test Runner Agent
│
└── Resource Manager (global, watches all projects)

BOOTSTRAP CORE (always running)
├── HR Agent
├── Prompt Engineer Agent
├── Tool Maker Agent
└── Memory Manager Agent

SHARED MEMORY (Layer 5)
├── ChromaDB (vector store)
└── Markdown Vault (structured notes)
```

---

## Role Summary Table

| Agent | Layer | Created by | Lifespan | Key responsibility |
|---|---|---|---|---|
| CEO / Orchestrator | 1 | Bootstrap (permanent) | Permanent | Goal → brief → approve → review |
| Project Manager | 2 | HR Agent | Per project | Runs one project end-to-end |
| Resource Manager | 2 | HR Agent | Permanent | Agent load across all projects |
| HR Agent | 3 Bootstrap | Permanent | Permanent | Team composition |
| Prompt Engineer | 3 Bootstrap | Permanent | Permanent | Agent system prompts |
| Tool Maker | 3 Bootstrap | Permanent | Permanent | Tool creation and versioning |
| Memory Manager | 3 Bootstrap | Permanent | Permanent | Knowledge graph ownership |
| Team Lead | 4 Dynamic | HR Agent | Per project | Domain ownership, tech decisions |
| Specialist Agent | 4 Dynamic | HR Agent + Prompt Engineer | Per project | Execution within domain |

---

## Scaling Rules

The HR Agent uses these rules to decide team structure:

```
Project scope = SMALL
  → Project Manager + 2-4 specialist agents (no team leads)
  → Example: "Add OAuth login to existing app"

Project scope = MEDIUM  
  → Project Manager + 2-3 Team Leads + agents under each
  → Example: "Build a REST API with auth and a dashboard"

Project scope = LARGE
  → Project Manager + full Team Lead set + multiple agents per lead
  → Example: "Build a full SaaS platform with web + mobile + API"
```

Scope is assessed by the CEO from the Project Brief before team formation begins.

---

## Decision Authority

| Decision | Authority level |
|---|---|
| What the overall goal is | Human |
| Project brief content | CEO |
| Team structure and composition | HR Agent → CEO approves |
| Tech stack for a domain | Team Lead → Project Manager → CEO (if novel) |
| Which framework/library to use | Team Lead (autonomous) |
| Agent definition changes (structural) | Prompt Engineer → Human approves |
| Agent prompt refinements | Prompt Engineer → CEO approves |
| New tool creation | Tool Maker → Human approves |
| Tool updates/patches | Tool Maker → CEO approves |

---

## Related Notes

- [[SYSTEM-OVERVIEW]]
- [[../02-Agents/CEO-ORCHESTRATOR]]
- [[../02-Agents/BOOTSTRAP-CORE]]
- [[../02-Agents/TEAM-LEAD]]
