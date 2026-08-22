from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from neuroforge.workflows.task_store import (
    load_all_task_results,
    load_task_result,
    save_task_result,
)


@patch("neuroforge.workflows.task_store.init_chroma")
@patch("neuroforge.workflows.task_store.get_collection")
def test_save_task_result_success(mock_get_coll, mock_init):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}
    mock_get_coll.return_value = mock_coll

    res = save_task_result(
        "proj1", "T1", {"summary": "Done"}, status="complete"
    )
    assert res is True
    mock_coll.add.assert_called_once()


@patch("neuroforge.workflows.task_store.init_chroma")
@patch("neuroforge.workflows.task_store.get_collection")
def test_save_task_result_upserts_existing(mock_get_coll, mock_init):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": ["proj1:task:T1"]}
    mock_get_coll.return_value = mock_coll

    res = save_task_result(
        "proj1", "T1", {"summary": "Done"}, status="complete"
    )
    assert res is True
    mock_coll.update.assert_called_once()


@patch("neuroforge.workflows.task_store.init_chroma")
@patch("neuroforge.workflows.task_store.get_collection")
def test_load_task_result_found(mock_get_coll, mock_init):
    mock_coll = MagicMock()
    result_data = {"summary": "Done", "status": "complete"}
    mock_coll.get.return_value = {
        "ids": ["proj1:task:T1"],
        "metadatas": [{"result_json": json.dumps(result_data)}],
    }
    mock_get_coll.return_value = mock_coll

    res = load_task_result("proj1", "T1")
    assert res == result_data


@patch("neuroforge.workflows.task_store.init_chroma")
@patch("neuroforge.workflows.task_store.get_collection")
def test_load_task_result_not_found(mock_get_coll, mock_init):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {"ids": []}
    mock_get_coll.return_value = mock_coll

    res = load_task_result("proj1", "T1")
    assert res is None


@patch("neuroforge.workflows.task_store.init_chroma")
@patch("neuroforge.workflows.task_store.get_collection")
def test_load_all_task_results_filters_by_project(mock_get_coll, mock_init):
    mock_coll = MagicMock()
    mock_coll.get.return_value = {
        "ids": ["p1:task:T1", "p1:task:T2", "p2:task:T1"],
        "metadatas": [
            {"result_json": json.dumps({"summary": "T1 done"})},
            {"result_json": json.dumps({"summary": "T2 done"})},
            {"result_json": json.dumps({"summary": "P2 T1 done"})},
        ],
    }
    mock_get_coll.return_value = mock_coll

    res = load_all_task_results("p1")
    assert len(res) == 2
    assert "T1" in res
    assert "T2" in res
    assert res["T1"]["summary"] == "T1 done"
