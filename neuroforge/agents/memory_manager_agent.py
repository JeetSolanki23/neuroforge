from __future__ import annotations

import json
from datetime import datetime, timezone

from neuroforge.agents.base import AgentInput, AgentOutput, BaseAgent
from neuroforge.memory.chroma import get_collection
from neuroforge.schemas.base import LearnedKnowledge, MemoryConfidence


class MemoryManagerAgent(BaseAgent):
    agent_id = "memory-manager-agent"
    name = "Memory Manager Agent"
    role = "Distills project experience into lasting learned knowledge"
    layer = "bootstrap"

    def _execute(self, input: AgentInput) -> AgentOutput:
        """input.task: JSON string — list of operational event dicts

        input.project_id: required Returns: AgentOutput with result = {
        "learned_entries": [...],     "summary": str,     "stored_count": int,
        "surface_to_human": [...] }
        """
        if not input.project_id:
            return AgentOutput(
                success=False,
                result=None,
                error="MemoryManagerAgent requires project_id",
            )

        raw = self._call_llm(
            messages=[self._build_message(input.task)],
            system=self.system_prompt,
            max_tokens=2000,
        )

        try:
            llm_result = json.loads(raw)
        except json.JSONDecodeError as e:
            return AgentOutput(
                success=False,
                result=None,
                error=f"Memory Manager returned invalid JSON: {e}\nRaw: {raw[:200]}",
            )

        if "learned_entries" not in llm_result:
            return AgentOutput(
                success=False,
                result=None,
                error="Memory Manager response missing 'learned_entries' key",
            )

        stored = []
        surface_to_human = []
        collection = get_collection("learned_knowledge")
        year = datetime.now(timezone.utc).strftime("%Y")

        for i, entry in enumerate(llm_result.get("learned_entries", [])):
            entry_id = f"LK-{year}-{input.project_id}-{i:03d}"
            try:
                lk = LearnedKnowledge(
                    id=entry_id,
                    created_at=datetime.now(timezone.utc),
                    title=entry.get("title", "Untitled"),
                    content=entry.get("content", ""),
                    domain=entry.get("domain", []),
                    applies_to_agents=entry.get("applies_to_agents", []),
                    confidence=MemoryConfidence(entry.get("confidence", "low")),
                    project_ids=[input.project_id],
                    tags=entry.get("tags", []),
                )

                collection.add(
                    ids=[entry_id],
                    documents=[f"{lk.title}\n\n{lk.content}"],
                    metadatas=[{
                        "project_id": input.project_id,
                        "domain": ",".join(lk.domain),
                        "confidence": lk.confidence.value,
                        "tags": ",".join(lk.tags),
                    }],
                )
                stored.append(lk.model_dump(mode="json"))

                if entry.get("surface_to_human"):
                    surface_to_human.append({
                        "id": entry_id,
                        "title": lk.title,
                        "reason": entry.get("surface_reason", ""),
                    })

            except Exception as e:
                self.logger.warning(
                    "memory_entry_store_failed", entry_id=entry_id, error=str(e)
                )
                continue

        return AgentOutput(
            success=True,
            result={
                "learned_entries": stored,
                "summary": llm_result.get("summary", ""),
                "stored_count": len(stored),
                "surface_to_human": surface_to_human,
            },
        )
