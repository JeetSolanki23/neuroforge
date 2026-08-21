from __future__ import annotations

import json

from neuroforge.agents.base import AgentInput, AgentOutput, BaseAgent


class HRAgent(BaseAgent):
    agent_id = "hr-agent"
    name = "HR Agent"
    role = "Composes project teams based on project brief"
    layer = "bootstrap"

    def _execute(self, input: AgentInput) -> AgentOutput:
        """input.task: JSON string of ProjectBrief dict input.context: optional

        {"available_agent_types": [...]} Returns: AgentOutput with result = team
        composition dict
        """
        content = input.task
        if input.context:
            available = input.context.get("available_agent_types", [])
            if available:
                content += (
                    f"\n\nAvailable agent types in registry: "
                    f"{json.dumps(available)}"
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
                error=f"HR Agent returned invalid JSON: {e}\nRaw: {raw[:200]}",
            )

        required = {
            "scope_assessment",
            "requires_team_leads",
            "specialists",
            "reasoning",
        }
        missing = required - result.keys()
        if missing:
            return AgentOutput(
                success=False,
                result=None,
                error=f"HR Agent response missing keys: {missing}",
            )

        return AgentOutput(success=True, result=result)
