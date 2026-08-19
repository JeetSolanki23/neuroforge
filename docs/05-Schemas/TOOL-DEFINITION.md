# Schema: Tool Definition

tags: #schema #tools #registry

---

## Overview

The Tool Definition is the canonical record of every tool in the system. Tools are the capabilities agents act through — reading files, running tests, calling APIs, committing code. Every tool that gets created by the Tool Maker is versioned, registered, and reusable across all agent types and projects.

---

## Full Schema

```json
{
  "schema_version": "1.0",

  "id": "run_tests",
  "version": "1.1.0",
  "created_by": "tool-maker-agent",
  "created_at": "2024-01-20T11:00:00Z",
  "last_updated": "2024-02-15T09:30:00Z",
  "update_reason": "Added pytest-cov coverage reporting support",
  "update_approved_by": "ceo-agent",
  "status": "active | deprecated | experimental",

  "identity": {
    "name": "Run Tests",
    "category": "test_tools",
    "description": "Runs a pytest test suite and returns structured results including pass/fail counts, coverage percentage, and individual failure details",
    "created_for_project": "project-todo-api-001"
  },

  "interface": {
    "function_name": "run_tests",
    "parameters": {
      "test_path": {
        "type": "string",
        "description": "Path to test file or directory",
        "required": true
      },
      "coverage": {
        "type": "bool",
        "description": "Whether to include coverage report",
        "default": true
      },
      "verbose": {
        "type": "bool",
        "description": "Whether to return full raw output",
        "default": false
      }
    },
    "returns": {
      "status": "passed | failed | error",
      "tests_run": "int",
      "passed": "int",
      "failed": "int",
      "errors": "int",
      "coverage_percent": "float | null",
      "failures": [
        {
          "test_name": "string",
          "error": "string",
          "line": "int | null"
        }
      ],
      "raw_output": "string | null"
    },
    "raises": [
      "ToolExecutionError — if pytest cannot be found or path is invalid",
      "TimeoutError — if test suite exceeds 300 seconds"
    ]
  },

  "implementation": {
    "file": "tools/test_tools/run_tests.py",
    "language": "python",
    "dependencies": ["pytest>=7.0", "pytest-cov>=4.0"],
    "requires_env": []
  },

  "access_control": {
    "agents_allowed": ["*"],
    "agents_denied": [],
    "requires_approval_to_use": false
  },

  "performance": {
    "times_called": 47,
    "error_rate": 0.02,
    "average_duration_seconds": 4.2,
    "last_called": "2024-03-25T11:00:00Z"
  },

  "evolution_log": [
    {
      "version": "1.0.0",
      "date": "2024-01-20",
      "type": "initial_creation",
      "approved_by": "human",
      "summary": "Initial creation — basic pytest runner, no coverage"
    },
    {
      "version": "1.1.0",
      "date": "2024-02-15",
      "type": "update",
      "approved_by": "ceo-agent",
      "summary": "Added pytest-cov integration for coverage reporting"
    }
  ],

  "tags": ["testing", "pytest", "python", "coverage", "test_tools"]
}
```

---

## Tool Categories

The Tool Maker organises all tools into categories. Every tool belongs to exactly one category:

| Category | Description | Examples |
|---|---|---|
| `file_tools` | Read, write, create, delete files and directories | `read_file`, `write_file`, `list_directory` |
| `code_tools` | Execute code, capture output, manage environments | `run_python`, `run_shell`, `pip_install` |
| `test_tools` | Run test suites, parse results, report failures | `run_tests`, `run_playwright`, `check_coverage` |
| `git_tools` | Version control operations | `git_commit`, `git_branch`, `create_pr` |
| `api_tools` | Call external APIs, handle auth and rate limits | `http_get`, `http_post`, `call_with_retry` |
| `search_tools` | Semantic search in memory, web search | `search_memory`, `web_search` |
| `system_tools` | Shell commands, environment variables, processes | `run_command`, `set_env`, `check_port` |
| `db_tools` | Database interactions | `run_migration`, `query_db`, `seed_db` |

---

## Versioning Rules

Semantic versioning: `MAJOR.MINOR.PATCH`

| Change type | Version bump | Approval needed |
|---|---|---|
| Bug fix (same interface, same behavior) | PATCH | CEO |
| New optional parameter added | MINOR | CEO |
| New return field added | MINOR | CEO |
| Interface change (breaking) | MAJOR | **Human** |
| New tool in existing category | v1.0.0 | CEO |
| New tool in **new** category | v1.0.0 | **Human** |

---

## Deprecation Policy

Old tool versions are never deleted — only marked `deprecated`. This ensures projects that were built with a specific tool version can always reproduce their exact behavior.

```json
{
  "id": "run_tests",
  "version": "1.0.0",
  "status": "deprecated",
  "deprecated_at": "2024-02-15",
  "deprecated_reason": "Superseded by v1.1.0 with coverage support",
  "use_instead": "run_tests@1.1.0"
}
```

---

## Storage Locations

**ChromaDB:** `tool_definitions` collection
- Document: full JSON schema
- Metadata: id, version, category, status, tags
- Embedding: generated from name + description + interface (for semantic search)

**Markdown Vault:** `memory-vault/tools/{tool-id}/v{version}.md`
- Human-readable version of the same data
- Linked in Obsidian graph view

**Implementation:** `neuroforge/tools/{category}/{tool-id}.py`
- Actual Python implementation
- Version tracked via Git

---

## How Agents Use Tools

Agents never call tool implementations directly. They call the tool via the tool registry interface, which handles version pinning, error wrapping, and logging:

```python
# Agent calls (pseudocode)
result = tool_registry.call(
    tool_id="run_tests",
    version="latest",        # or pin to "1.0.0" for reproducibility
    params={
        "test_path": "./tests/",
        "coverage": True
    }
)

if result.status == "failed":
    # handle failures, escalate if needed
```

Every tool call is automatically logged to operational memory by the registry — agents don't need to log it themselves.

---

## Related Notes

- [[../02-Agents/BOOTSTRAP-CORE]]
- [[../04-Workflows/AGENT-CREATION]]
- [[../04-Workflows/EVOLUTION-CYCLE]]
- [[AGENT-DEFINITION]]
- [[MEMORY-ENTRY]]
