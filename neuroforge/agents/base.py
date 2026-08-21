from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from neuroforge.config import config
from neuroforge.llm.client import call_llm
from neuroforge.logger import get_logger


@dataclass
class AgentInput:
    task: str
    context: dict = field(default_factory=dict)
    project_id: str | None = None


@dataclass
class AgentOutput:
    success: bool
    result: Any
    error: str | None = None
    escalate: bool = False
    escalation_reason: str | None = None


class BaseAgent(ABC):
    agent_id: str  # must be set by subclass — matches registry id
    name: str
    role: str
    layer: str  # bootstrap | management | orchestration | dynamic

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.max_retries = config.MAX_TASK_RETRIES
        self._definition: dict | None = None  # loaded from registry lazily

    def get_definition(self) -> dict:
        """Load this agent's definition from ChromaDB registry.

        Cached after first load. Returns the full definition dict.
        Raises RuntimeError if agent not found in registry.
        """
        if self._definition is None:
            from neuroforge.agents.registry import load_agent_definition

            self._definition = load_agent_definition(self.agent_id)
        return self._definition

    @property
    def system_prompt(self) -> str:
        return self.get_definition()["system_prompt"]

    @property
    def must_not(self) -> list[str]:
        return self.get_definition().get("must_not", [])

    @property
    def must_always(self) -> list[str]:
        return self.get_definition().get("must_always", [])

    @property
    def escalate_if(self) -> list[str]:
        return self.get_definition().get("escalate_if", [])

    def run(self, input: AgentInput) -> AgentOutput:
        """Public entry point.

        Handles retry logic and logging. Calls _execute() which subclasses
        implement.
        """
        self.logger.info("agent_run_start", agent=self.agent_id, task=input.task[:80])
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                output = self._execute(input)
                if output.success:
                    self.logger.info("agent_run_success", agent=self.agent_id, attempt=attempt)
                    return output
                else:
                    last_error = output.error
                    self.logger.warning(
                        "agent_run_attempt_failed",
                        agent=self.agent_id,
                        attempt=attempt,
                        error=last_error,
                    )
            except Exception as e:
                last_error = str(e)
                self.logger.error(
                    "agent_run_exception",
                    agent=self.agent_id,
                    attempt=attempt,
                    error=last_error,
                )

        self.logger.error(
            "agent_run_exhausted_retries",
            agent=self.agent_id,
            max_retries=self.max_retries,
        )
        return AgentOutput(
            success=False,
            result=None,
            error=f"Failed after {self.max_retries} attempts. Last: {last_error}",
            escalate=True,
            escalation_reason=f"Max retries exhausted: {last_error}",
        )

    @abstractmethod
    def _execute(self, input: AgentInput) -> AgentOutput:
        pass

    def _call_llm(
        self, messages: list[dict], system: str, max_tokens: int = 1024
    ) -> str:
        return call_llm(messages=messages, system=system, max_tokens=max_tokens)

    def _build_message(self, content: str, role: str = "user") -> dict:
        return {"role": role, "content": content}
