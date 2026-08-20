from __future__ import annotations

import json

from neuroforge.agents.base import AgentInput, AgentOutput, BaseAgent


class PromptEngineerAgent(BaseAgent):
    agent_id = "prompt-engineer-agent"
    name = "Prompt Engineer Agent"
    role = "Writes and refines system prompts for all agent types"
    layer = "bootstrap"

    def _execute(self, input: AgentInput) -> AgentOutput:
        """input.task: description of agent type, role, domain, project context

        Returns: AgentOutput with result = prompt spec dict
        """
        raw = self._call_llm(
            messages=[self._build_message(input.task)],
            system=self.system_prompt,
            max_tokens=2000,
        )

        try:
            result = json.loads(raw)
        except json.JSONDecodeError as e:
            return AgentOutput(
                success=False,
                result=None,
                error=f"Prompt Engineer returned invalid JSON: {e}\nRaw: {raw[:200]}",
            )

        if "system_prompt" not in result:
            return AgentOutput(
                success=False,
                result=None,
                error="Prompt Engineer response missing 'system_prompt' key",
            )

        return AgentOutput(success=True, result=result)
