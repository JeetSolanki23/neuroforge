# CEO / Orchestrator Agent

tags: #agent #orchestration #permanent

---

## Role Summary

The CEO is the entry point for every goal. It never writes code, never picks a framework, and never manages individual agent tasks. Its job is to think at the **goal and outcome level** — what needs to exist, why, and whether what was built actually achieves it.

---

## Responsibilities

### On goal receipt
1. Parse the human's natural language goal
2. Identify ambiguities and resolve them (ask human if needed)
3. Query shared memory for similar past projects
4. Produce a structured [[../05-Schemas/PROJECT-BRIEF|Project Brief]]
5. Assess project scope (small / medium / large)
6. Hand brief to Project Manager agent

### On team formation
1. Receive proposed team structure from HR Agent (via Project Manager)
2. Review team composition against project brief
3. Approve team or request adjustments
4. If any new agent type is proposed → flag for human approval before proceeding

### During execution
1. Receive status reports from Project Manager only (not individual agents)
2. Resolve escalations that Project Manager cannot handle
3. Make calls on novel tech stack decisions surfaced by Team Leads
4. Never intervene in domain-level decisions unless escalated

### On project close
1. Receive Memory Manager's end-of-project report
2. Review distilled learnings list
3. Decide which learnings are review-worthy → surface to human if yes
4. Approve any agent definition changes proposed by Prompt Engineer
5. Sign off on project completion

### On long-running projects
- Receives mid-project memory reports when volume of logged decisions crosses threshold
- Applies same review logic as end-of-project reports

---

## What the CEO Does NOT Do

- Does not talk directly to specialist agents
- Does not select frameworks, libraries, or tools
- Does not manage task-level scheduling (that's Project Manager)
- Does not track individual agent availability (that's Resource Manager)
- Does not write agent prompts (that's Prompt Engineer)
- Does not decide what to store in memory (that's Memory Manager)

---

## Decision Authority

| Decision | CEO action |
|---|---|
| Novel agent type needed | Flag to human, await approval |
| Known agent type needed | Approve autonomously |
| New tool needed | Flag to human, await approval |
| Tool update/patch | Approve autonomously |
| Agent prompt refinement | Approve autonomously |
| Tech stack (familiar) | Approve autonomously |
| Tech stack (novel/unfamiliar) | Surface to human |
| Memory learning → review | Decide whether to surface to human |

---

## Internal Flow (LangGraph nodes)

```
[goal_intake]
    → parse goal
    → check memory for similar projects
    → identify ambiguities
    ↓
[brief_generation]
    → produce Project Brief
    → assess scope
    ↓
[team_approval]
    → receive proposed team from HR
    → approve / request changes
    → flag novel agent types to human
    ↓
[execution_supervision]
    → receive Project Manager status updates
    → resolve escalations
    ↓
[project_close]
    → receive Memory Manager report
    → review learnings
    → approve agent updates
    → surface to human if warranted
```

---

## Escalation Triggers

The CEO escalates to the human when:
- A completely new type of agent is needed (never been created before)
- A new tool is needed
- A tech stack decision is genuinely novel
- A project is blocked in a way the CEO cannot resolve
- Memory Manager flags learnings as human-review-worthy

---

## Context Packet (what it receives per call)

```json
{
  "human_goal": "string — raw input",
  "similar_projects": ["array of past project briefs from memory"],
  "current_agent_registry": ["list of available agent types"],
  "current_tool_registry": ["list of available tools"],
  "active_projects": ["list of projects currently running"],
  "escalation_if_present": "object — what triggered this call mid-project"
}
```

---

## Related Notes

- [[../01-Architecture/AGENT-HIERARCHY]]
- [[../04-Workflows/GOAL-TO-SOFTWARE]]
- [[../05-Schemas/PROJECT-BRIEF]]
- [[PROJECT-MANAGER]]
