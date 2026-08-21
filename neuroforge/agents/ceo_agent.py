from __future__ import annotations

import json

from neuroforge.agents.base import AgentInput, AgentOutput, BaseAgent


class CEOAgent(BaseAgent):
    agent_id = "ceo-orchestrator"
    name = "CEO / Orchestrator"
    role = "Receives goals, produces project briefs, approves teams, reviews outcomes"
    layer = "orchestration"

    def _execute(self, input: AgentInput) -> AgentOutput:
        """input.task: JSON string with {"goal": str, "similar_projects": [...]}

        Returns: AgentOutput with result = ProjectBrief dict
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
                error=f"CEO returned invalid JSON: {e}\nRaw: {raw[:200]}",
            )

        required = {
            "raw_goal",
            "parsed_intent",
            "scope",
            "functional_requirements",
            "acceptance_criteria",
        }
        missing = required - result.keys()
        if missing:
            return AgentOutput(
                success=False,
                result=None,
                error=f"CEO response missing keys: {missing}",
            )

        valid_scopes = {"small", "medium", "large"}
        if result.get("scope") not in valid_scopes:
            return AgentOutput(
                success=False,
                result=None,
                error=f"CEO returned invalid scope: {result.get('scope')}",
            )

        return AgentOutput(success=True, result=result)
