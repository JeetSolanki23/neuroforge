from __future__ import annotations

from langgraph.graph import END, StateGraph

from neuroforge.workflows.nodes import (
    _route_after_briefing,
    _route_after_execution,
    _route_after_task,
    _route_after_team_formation,
    briefing_node,
    execute_single_task,
    execution_node,
    review_node,
    team_formation_node,
)
from neuroforge.workflows.state import ProjectState


def build_project_graph():
    """Builds and compiles the project execution LangGraph.

    Graph structure:
    START → briefing → [team_formation | END]
         → [execution | END]
         → execute_single_task (parallel, fan-out via Send)
         → [execute_single_task (more waves) | review]
         → END
    """
    graph = StateGraph(ProjectState)

    graph.add_node("briefing", briefing_node)
    graph.add_node("team_formation", team_formation_node)
    graph.add_node("execution", execution_node)
    graph.add_node("execute_single_task", execute_single_task)
    graph.add_node("review", review_node)

    graph.set_entry_point("briefing")

    graph.add_conditional_edges(
        "briefing",
        _route_after_briefing,
        {"team_formation": "team_formation", "end": END},
    )
    graph.add_conditional_edges(
        "team_formation",
        _route_after_team_formation,
        {"execution": "execution", "end": END},
    )

    # execution_node builds DAG; _route_after_execution dispatches first wave via Send
    graph.add_conditional_edges(
        "execution",
        _route_after_execution,
        {
            "execute_single_task": "execute_single_task",
            "review": "review",
            "end": END,
        },
    )

    # After each task: check for more ready tasks or go to review
    graph.add_conditional_edges(
        "execute_single_task",
        _route_after_task,
        {
            "execute_single_task": "execute_single_task",
            "review": "review",
        },
    )

    graph.add_edge("review", END)
    return graph.compile()
