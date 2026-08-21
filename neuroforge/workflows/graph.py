from __future__ import annotations

from langgraph.graph import END, StateGraph

from neuroforge.workflows.nodes import (
    _route_after_briefing,
    _route_after_execution,
    _route_after_team_formation,
    briefing_node,
    execution_node,
    review_node,
    team_formation_node,
)
from neuroforge.workflows.state import ProjectState


def build_project_graph():
    """Builds and compiles the project execution LangGraph.

    Returns a compiled graph ready to invoke.

    Graph structure:
    START → briefing → [team_formation | END] →
            [execution | END] → review → END
    """
    graph = StateGraph(ProjectState)

    # Add nodes
    graph.add_node("briefing", briefing_node)
    graph.add_node("team_formation", team_formation_node)
    graph.add_node("execution", execution_node)
    graph.add_node("review", review_node)

    # Entry point
    graph.set_entry_point("briefing")

    # Conditional edges
    graph.add_conditional_edges(
        "briefing",
        _route_after_briefing,
        {
            "team_formation": "team_formation",
            "end": END,
        },
    )
    graph.add_conditional_edges(
        "team_formation",
        _route_after_team_formation,
        {
            "execution": "execution",
            "end": END,
        },
    )
    graph.add_conditional_edges(
        "execution",
        _route_after_execution,
        {
            "review": "review",
            "end": END,
        },
    )

    # Review always ends
    graph.add_edge("review", END)

    return graph.compile()
