from __future__ import annotations

import json

from neuroforge.agents.base import AgentInput, AgentOutput, BaseAgent
from neuroforge.agents.registry import load_agent_definition
from neuroforge.logger import get_logger

logger = get_logger("specialist_agent")


class SpecialistAgent(BaseAgent):
    """Dynamic specialist agent created per task.

    System prompt is the base template with context injected. agent_id is set
    dynamically based on the role being played.
    """

    def __init__(self, role: str, domain: str, project_context: dict):
        """role: e.g. "backend-django-specialist" domain: e.g. "backend"

        project_context: dict with project_name, constraints,
                         relevant_memory etc.
        """
        super().__init__()
        self.agent_id = f"specialist-{domain}"
        self.name = f"{role} Specialist"
        self.role = role
        self.layer = "dynamic"
        self.domain = domain
        self.project_context = project_context
        self._role_name = role

    def get_definition(self) -> dict:
        """Load base template from registry."""
        if self._definition is None:
            self._definition = load_agent_definition(
                "specialist-base-template"
            )
        return self._definition

    def _build_system_prompt(self, task_description: str) -> str:
        """Inject context into the base template system prompt."""
        template = self.get_definition()["system_prompt"]
        return template.format(
            role=self._role_name,
            domain=self.domain,
            project_name=self.project_context.get("project_name", "Unknown"),
            task_description=task_description,
            project_context=json.dumps(
                self.project_context.get("brief_summary", {}), indent=2
            ),
            constraints="\n".join(
                f"- {c}"
                for c in self.project_context.get("constraints", [])
            )
            or "None specified",
        )

    def _execute(self, input: AgentInput) -> AgentOutput:
        """input.task: the task description string input.context: optional

        additional context dict Returns: AgentOutput with result = task result
        dict
        """
        system_prompt = self._build_system_prompt(input.task)

        raw = self._call_llm(
            messages=[self._build_message(input.task)],
            system=system_prompt,
            max_tokens=4096,
        )

        try:
            result = json.loads(raw)
        except json.JSONDecodeError as e:
            return AgentOutput(
                success=False,
                result=None,
                error=f"Specialist returned invalid JSON: {e}\nRaw: {raw[:300]}",
            )

        required = {"status", "result", "summary"}
        missing = required - result.keys()
        if missing:
            return AgentOutput(
                success=False,
                result=None,
                error=f"Specialist response missing keys: {missing}",
            )

        if result.get("status") == "blocked":
            return AgentOutput(
                success=False,
                result=result,
                error=f"Task blocked: {result.get('blockers', [])}",
                escalate=True,
                escalation_reason=f"Specialist blocked: {result.get('blockers')}",
            )

        if result.get("status") == "failed":
            return AgentOutput(
                success=False,
                result=result,
                error=f"Specialist reported failure: {result.get('summary')}",
            )

        return AgentOutput(success=True, result=result)
