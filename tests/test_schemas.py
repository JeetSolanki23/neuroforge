from datetime import datetime
from neuroforge.schemas.base import (
    AgentDefinition,
    AgentLayer,
    LearnedKnowledge,
    MemoryConfidence,
    ProjectBrief,
    ProjectScope,
    ResourceStatus,
    ToolCategory,
    ToolDefinition,
)


def test_project_brief_instantiation():
    now = datetime.now()
    brief = ProjectBrief(
        id="proj-1",
        created_at=now,
        raw_goal="Build API",
        parsed_intent="Build a REST API",
        scope=ProjectScope.SMALL,
    )
    assert brief.id == "proj-1"
    assert brief.scope == ProjectScope.SMALL
    assert brief.functional_requirements == []


def test_agent_definition_instantiation():
    now = datetime.now()
    agent = AgentDefinition(
        id="agent-1",
        created_at=now,
        layer=AgentLayer.BOOTSTRAP,
        name="HR Agent",
        role="HR",
        domain="management",
        system_prompt="Prompt",
    )
    assert agent.id == "agent-1"
    assert agent.layer == AgentLayer.BOOTSTRAP
    assert agent.version == "1.0.0"


def test_tool_definition_instantiation():
    now = datetime.now()
    tool = ToolDefinition(
        id="tool-1",
        created_at=now,
        category=ToolCategory.FILE_TOOLS,
        name="Read File",
        description="Reads a file",
        function_name="read_file",
        file_path="tools/file_tools.py",
    )
    assert tool.id == "tool-1"
    assert tool.category == ToolCategory.FILE_TOOLS


def test_learned_knowledge_instantiation():
    now = datetime.now()
    lk = LearnedKnowledge(
        id="lk-1",
        created_at=now,
        title="Title",
        content="Content",
        domain=["backend"],
    )
    assert lk.id == "lk-1"
    assert lk.confidence == MemoryConfidence.LOW


def test_project_scope_enum():
    assert set(ProjectScope) == {ProjectScope.SMALL, ProjectScope.MEDIUM, ProjectScope.LARGE}
    assert ProjectScope.SMALL == "small"
    assert ProjectScope.MEDIUM == "medium"
    assert ProjectScope.LARGE == "large"


def test_tool_category_enum():
    categories = {
        ToolCategory.FILE_TOOLS,
        ToolCategory.CODE_TOOLS,
        ToolCategory.TEST_TOOLS,
        ToolCategory.GIT_TOOLS,
        ToolCategory.API_TOOLS,
        ToolCategory.SEARCH_TOOLS,
        ToolCategory.SYSTEM_TOOLS,
        ToolCategory.DB_TOOLS,
    }
    assert len(categories) == 8
