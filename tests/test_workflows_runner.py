from __future__ import annotations

from unittest.mock import MagicMock, patch

from neuroforge.workflows.runner import run_project


@patch("neuroforge.workflows.runner.save_project_state")
@patch("neuroforge.workflows.runner.build_project_graph")
def test_run_project_returns_final_state(mock_build_graph, mock_save):
    mock_graph = MagicMock()
    expected_state = {
        "project_id": "proj-1",
        "current_phase": "complete",
        "messages": [],
    }
    mock_graph.invoke.return_value = expected_state
    mock_build_graph.return_value = mock_graph

    res = run_project("Build app")
    assert res["current_phase"] == "complete"


@patch("neuroforge.workflows.runner.save_project_state")
@patch("neuroforge.workflows.runner.build_project_graph")
def test_run_project_generates_unique_project_id(mock_build_graph, mock_save):
    mock_graph = MagicMock()
    mock_graph.invoke.side_effect = lambda state: state
    mock_build_graph.return_value = mock_graph

    res1 = run_project("Goal 1")
    res2 = run_project("Goal 2")
    assert res1["project_id"] != res2["project_id"]


@patch("neuroforge.workflows.runner.save_project_state")
@patch("neuroforge.workflows.runner.build_project_graph")
def test_run_project_handles_graph_exception(mock_build_graph, mock_save):
    mock_graph = MagicMock()
    mock_graph.invoke.side_effect = RuntimeError("Graph execution crashed")
    mock_build_graph.return_value = mock_graph

    res = run_project("Crash goal")
    assert res["current_phase"] == "failed"
    assert "Graph execution crashed" in res["error"]
