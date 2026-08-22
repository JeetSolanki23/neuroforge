from __future__ import annotations

import json
from datetime import datetime, timezone

from neuroforge.agents.base import AgentInput, AgentOutput, BaseAgent
from neuroforge.config import config
from neuroforge.logger import get_logger
from neuroforge.memory.chroma import get_collection, init_chroma

logger = get_logger("resource_manager")

RESOURCE_COLLECTION = "project_memory"
RESOURCE_DOC_PREFIX = "resource:"


class ResourceManager(BaseAgent):
    agent_id = "resource-manager"
    name = "Resource Manager"
    role = "Tracks agent instance load across all active projects"
    layer = "management"

    # ResourceManager does NOT load from ChromaDB registry —
    # it has no system prompt (it doesn't make LLM calls).
    # Override get_definition to return a stub.
    def get_definition(self) -> dict:
        return {
            "system_prompt": "",
            "must_not": [],
            "must_always": [],
            "escalate_if": [],
        }

    def _execute(self, input: AgentInput) -> AgentOutput:
        """Routes to the right action based on input.task value:

        "check:{agent_type}"   → check availability
        "assign:{agent_type}:{project_id}"  → assign instance
        "release:{agent_type}:{project_id}" → release instance "status" →
        return full load report
        """
        task = input.task.strip()

        if task.startswith("check:"):
            agent_type = task.split(":", 1)[1]
            return self._check_availability(agent_type)

        elif task.startswith("assign:"):
            parts = task.split(":")
            if len(parts) < 3:
                return AgentOutput(
                    success=False,
                    result=None,
                    error="assign requires format: assign:{agent_type}:{project_id}",
                )
            return self._assign_instance(parts[1], parts[2])

        elif task.startswith("release:"):
            parts = task.split(":")
            if len(parts) < 3:
                return AgentOutput(
                    success=False,
                    result=None,
                    error="release requires format: release:{agent_type}:{project_id}",
                )
            return self._release_instance(parts[1], parts[2])

        elif task == "status":
            return self._get_status()

        else:
            return AgentOutput(
                success=False,
                result=None,
                error=f"Unknown ResourceManager task: {task}",
            )

    def _check_availability(self, agent_type: str) -> AgentOutput:
        """Returns whether an idle instance is available."""
        instances = self._load_instances(agent_type)
        idle = [i for i in instances if i["status"] == "idle"]
        queued = [i for i in instances if i["status"] == "active"]
        max_inst = config.MAX_INSTANCES_PER_AGENT_TYPE

        return AgentOutput(
            success=True,
            result={
                "agent_type": agent_type,
                "idle_count": len(idle),
                "active_count": len(queued),
                "can_spawn": len(instances) < max_inst,
                "available": len(idle) > 0 or len(instances) < max_inst,
            },
        )

    def _assign_instance(self, agent_type: str, project_id: str) -> AgentOutput:
        """Assigns an idle instance to a project, or registers a new one if
        under MAX_INSTANCES_PER_AGENT_TYPE.

        Returns the instance_id assigned.
        """
        instances = self._load_instances(agent_type)
        max_inst = config.MAX_INSTANCES_PER_AGENT_TYPE

        # Use idle instance if available
        for inst in instances:
            if inst["status"] == "idle":
                inst["status"] = "active"
                inst["current_project"] = project_id
                inst["assigned_since"] = datetime.now(timezone.utc).isoformat()
                self._save_instances(agent_type, instances)
                return AgentOutput(
                    success=True,
                    result={"instance_id": inst["instance_id"], "reused": True},
                )

        # Spawn new if under limit
        if len(instances) < max_inst:
            instance_id = f"{agent_type}-{len(instances) + 1:02d}"
            new_inst = {
                "instance_id": instance_id,
                "agent_type": agent_type,
                "status": "active",
                "current_project": project_id,
                "assigned_since": datetime.now(timezone.utc).isoformat(),
                "projects_completed": 0,
            }
            instances.append(new_inst)
            self._save_instances(agent_type, instances)
            return AgentOutput(
                success=True,
                result={"instance_id": instance_id, "reused": False},
            )

        # At capacity — queue
        return AgentOutput(
            success=False,
            result={"agent_type": agent_type, "queued": True},
            error=f"All {max_inst} instances of {agent_type} are active. Queued.",
            escalate=False,
        )

    def _release_instance(self, agent_type: str, project_id: str) -> AgentOutput:
        """Marks an instance idle when its project completes."""
        instances = self._load_instances(agent_type)
        released = False

        for inst in instances:
            if inst.get("current_project") == project_id:
                inst["status"] = "idle"
                inst["current_project"] = None
                inst["assigned_since"] = None
                inst["projects_completed"] = inst.get("projects_completed", 0) + 1
                released = True
                break

        if released:
            self._save_instances(agent_type, instances)
            return AgentOutput(success=True, result={"released": True})

        return AgentOutput(
            success=False,
            result=None,
            error=f"No active instance of {agent_type} found for project {project_id}",
        )

    def _get_status(self) -> AgentOutput:
        """Returns full load report across all agent types."""
        try:
            init_chroma()
            collection = get_collection(RESOURCE_COLLECTION)
            results = collection.get(include=["ids", "metadatas"])
            resource_docs = [
                {
                    "agent_type": m.get("agent_type"),
                    "instances": json.loads(m.get("instances_json", "[]")),
                }
                for doc_id, m in zip(
                    results.get("ids", []), results.get("metadatas", [])
                )
                if doc_id.startswith(RESOURCE_DOC_PREFIX)
            ]
            return AgentOutput(success=True, result=resource_docs)
        except Exception as e:
            return AgentOutput(
                success=False, result=None, error=f"Status check failed: {e}"
            )

    def _load_instances(self, agent_type: str) -> list[dict]:
        """Loads instance list for an agent type from ChromaDB."""
        try:
            init_chroma()
            collection = get_collection(RESOURCE_COLLECTION)
            doc_id = f"{RESOURCE_DOC_PREFIX}{agent_type}"
            results = collection.get(ids=[doc_id], include=["metadatas"])
            if not results["ids"]:
                return []
            return json.loads(results["metadatas"][0].get("instances_json", "[]"))
        except Exception:
            return []

    def _save_instances(self, agent_type: str, instances: list[dict]) -> None:
        """Saves instance list for an agent type to ChromaDB."""
        try:
            init_chroma()
            collection = get_collection(RESOURCE_COLLECTION)
            doc_id = f"{RESOURCE_DOC_PREFIX}{agent_type}"
            metadata = {
                "agent_type": agent_type,
                "instances_json": json.dumps(instances),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            existing = collection.get(ids=[doc_id])
            if existing["ids"]:
                collection.update(
                    ids=[doc_id],
                    documents=[f"resource:{agent_type}"],
                    metadatas=[metadata],
                )
            else:
                collection.add(
                    ids=[doc_id],
                    documents=[f"resource:{agent_type}"],
                    metadatas=[metadata],
                )
        except Exception as e:
            logger.error(
                "save_instances_failed", agent_type=agent_type, error=str(e)
            )
