from __future__ import annotations

from unittest.mock import patch

from neuroforge.workflows.vault_writer import (
    write_project_brief,
    write_project_summary,
)


def test_write_project_summary_creates_file(tmp_path):
    with patch("neuroforge.workflows.vault_writer.config") as mock_config:
        mock_config.MEMORY_VAULT_PATH = str(tmp_path)
        res = write_project_summary(
            project_id="p1",
            goal="Test Goal",
            brief={"scope": "small", "parsed_intent": "Parsed Goal"},
            task_results={
                "T1": {"status": "complete", "summary": "Finished T1"}
            },
            completed_task_ids=["T1"],
            failed_task_ids=[],
        )
        assert res is True
        outcomes_file = tmp_path / "projects" / "p1" / "outcomes.md"
        assert outcomes_file.exists()


def test_write_project_summary_content(tmp_path):
    with patch("neuroforge.workflows.vault_writer.config") as mock_config:
        mock_config.MEMORY_VAULT_PATH = str(tmp_path)
        write_project_summary(
            project_id="p1",
            goal="Test Goal",
            brief={"scope": "small", "parsed_intent": "Parsed Goal"},
            task_results={
                "T1": {
                    "status": "complete",
                    "summary": "Finished T1",
                    "decisions_made": ["Decision A"],
                }
            },
            completed_task_ids=["T1"],
            failed_task_ids=[],
        )
        outcomes_file = tmp_path / "projects" / "p1" / "outcomes.md"
        content = outcomes_file.read_text(encoding="utf-8")
        assert "project_id: p1" in content
        assert "Test Goal" in content
        assert "Finished T1" in content
        assert "Decision A" in content


def test_write_project_brief_creates_file(tmp_path):
    with patch("neuroforge.workflows.vault_writer.config") as mock_config:
        mock_config.MEMORY_VAULT_PATH = str(tmp_path)
        res = write_project_brief(
            project_id="p1",
            goal="Test Goal",
            brief={
                "scope": "small",
                "parsed_intent": "Parsed Goal",
                "functional_requirements": ["Req 1"],
                "acceptance_criteria": ["Crit 1"],
            },
        )
        assert res is True
        brief_file = tmp_path / "projects" / "p1" / "brief.md"
        assert brief_file.exists()


def test_write_project_brief_content(tmp_path):
    with patch("neuroforge.workflows.vault_writer.config") as mock_config:
        mock_config.MEMORY_VAULT_PATH = str(tmp_path)
        write_project_brief(
            project_id="p1",
            goal="Test Goal",
            brief={
                "scope": "small",
                "parsed_intent": "Parsed Goal",
                "functional_requirements": ["Req 1"],
                "acceptance_criteria": ["Crit 1"],
                "constraints": ["Constraint 1"],
            },
        )
        brief_file = tmp_path / "projects" / "p1" / "brief.md"
        content = brief_file.read_text(encoding="utf-8")
        assert "Req 1" in content
        assert "Crit 1" in content
        assert "Constraint 1" in content


def test_write_project_summary_silent_on_failure():
    with patch("neuroforge.workflows.vault_writer.Path") as mock_path:
        mock_path.side_effect = Exception("Disk error")
        res = write_project_summary(
            project_id="p1",
            goal="Goal",
            brief={},
            task_results={},
            completed_task_ids=[],
            failed_task_ids=[],
        )
        assert res is False
