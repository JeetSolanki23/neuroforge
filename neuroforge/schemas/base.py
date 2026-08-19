from __future__ import annotations

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ProjectScope(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    COMPLETE = "complete"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"


class AgentLayer(str, Enum):
    BOOTSTRAP = "bootstrap"
    DYNAMIC = "dynamic"
    MANAGEMENT = "management"
    ORCHESTRATION = "orchestration"


class ResourceStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"


class ToolCategory(str, Enum):
    FILE_TOOLS = "file_tools"
    CODE_TOOLS = "code_tools"
    TEST_TOOLS = "test_tools"
    GIT_TOOLS = "git_tools"
    API_TOOLS = "api_tools"
    SEARCH_TOOLS = "search_tools"
    SYSTEM_TOOLS = "system_tools"
    DB_TOOLS = "db_tools"


class MemoryConfidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CONFIRMED = "confirmed"


class ProjectBrief(BaseModel):
    id: str
    created_at: datetime
    status: ProjectStatus = ProjectStatus.ACTIVE
    raw_goal: str
    parsed_intent: str
    scope: ProjectScope
    functional_requirements: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    similar_project_ids: list[str] = Field(default_factory=list)
    team_approved: bool = False


class AgentEvolutionEntry(BaseModel):
    version: str
    date: str
    type: str
    approved_by: str
    summary: str


class AgentDefinition(BaseModel):
    id: str
    version: str = "1.0.0"
    created_at: datetime
    status: ResourceStatus = ResourceStatus.ACTIVE
    layer: AgentLayer
    name: str
    role: str
    domain: str
    system_prompt: str
    tools: list[str] = Field(default_factory=list)
    must_not: list[str] = Field(default_factory=list)
    must_always: list[str] = Field(default_factory=list)
    escalate_if: list[str] = Field(default_factory=list)
    projects_used_in: int = 0
    success_rate: float = 0.0
    evolution_log: list[AgentEvolutionEntry] = Field(default_factory=list)


class ToolDefinition(BaseModel):
    id: str
    version: str = "1.0.0"
    created_at: datetime
    status: ResourceStatus = ResourceStatus.ACTIVE
    category: ToolCategory
    name: str
    description: str
    function_name: str
    parameters: dict = Field(default_factory=dict)
    file_path: str
    dependencies: list[str] = Field(default_factory=list)
    times_called: int = 0
    error_rate: float = 0.0
    evolution_log: list[AgentEvolutionEntry] = Field(default_factory=list)


class LearnedKnowledge(BaseModel):
    id: str
    created_at: datetime
    title: str
    content: str
    domain: list[str]
    applies_to_agents: list[str] = Field(default_factory=list)
    confidence: MemoryConfidence = MemoryConfidence.LOW
    occurrence_count: int = 1
    project_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
