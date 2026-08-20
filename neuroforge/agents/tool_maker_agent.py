from __future__ import annotations

import json

from neuroforge.agents.base import AgentInput, AgentOutput, BaseAgent

VALID_CATEGORIES = {
    "file_tools",
    "code_tools",
    "test_tools",
    "git_tools",
    "api_tools",
    "search_tools",
    "system_tools",
    "db_tools",
}


class ToolMakerAgent(BaseAgent):
    agent_id = "tool-maker-agent"
    name = "Tool Maker Agent"
    role = "Designs tool specifications for capabilities agents need"
    layer = "bootstrap"

    def _execute(self, input: AgentInput) -> AgentOutput:
        """input.task: description of capability needed and why input.context:

        optional {"existing_tools": [...]} Returns: AgentOutput with result =
        tool specification dict
        """
        content = input.task
        if input.context:
            existing = input.context.get("existing_tools", [])
            if existing:
                content += (
                    f"\n\nExisting tools (do not duplicate): "
                    f"{json.dumps(existing)}"
                )

        raw = self._call_llm(
            messages=[self._build_message(content)],
            system=self.system_prompt,
            max_tokens=1500,
        )

        try:
            result = json.loads(raw)
        except json.JSONDecodeError as e:
            return AgentOutput(
                success=False,
                result=None,
                error=f"Tool Maker returned invalid JSON: {e}\nRaw: {raw[:200]}",
            )

        required = {"tool_id", "name", "category", "description", "function_name"}
        missing = required - result.keys()
        if missing:
            return AgentOutput(
                success=False,
                result=None,
                error=f"Tool Maker response missing keys: {missing}",
            )

        if result.get("category") not in VALID_CATEGORIES:
            return AgentOutput(
                success=False,
                result=None,
                error=f"Tool Maker returned invalid category: {result.get('category')}",
            )

        return AgentOutput(success=True, result=result)
