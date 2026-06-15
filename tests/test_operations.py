from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from sp_webdav_tool.models import SpData
from sp_webdav_tool.operations import SpOperations
from sp_webdav_tool.settings import Settings

FIXTURE = Path(__file__).parent / "fixtures" / "main_minimal.json"
FIXTURE_TEXT = FIXTURE.read_text(encoding="utf-8")

def make_mock_operations() -> tuple[SpOperations, MagicMock]:
    settings = Settings(
        url="https://sp.test:51434",
        path="/webdav/MAIN.json",
        username="user",
        password="pass",  # type: ignore[arg-type]
        timeout=10.0,
        retry_count=2,
    )

    ops = SpOperations.__new__(SpOperations)
    ops.settings = settings
    mock_client: Any = MagicMock()
    ops.client = mock_client
    mock_client.fetch.return_value = (
        SpData.model_validate_json(FIXTURE_TEXT),
        '"etag"',
    )
    mock_client.mutate.side_effect = lambda mutator, make_backup=False: _run_mutator(
        mutator
    )
    return ops, mock_client

def _run_mutator(mutator: Callable[[SpData], None]) -> SpData:
    data = SpData.model_validate_json(FIXTURE_TEXT)
    mutator(data)
    return data

def test_list_tasks_excludes_done() -> None:
    ops, _ = make_mock_operations()
    tasks = ops.list_tasks(include_done=False)
    assert all(not task.isDone for task in tasks)

def test_list_tasks_includes_done() -> None:
    ops, _ = make_mock_operations()
    tasks = ops.list_tasks(include_done=True)
    assert any(task.isDone for task in tasks)

def test_add_task_calls_mutate() -> None:
    ops, mock_client = make_mock_operations()
    task = ops.add_task("New task", project_id="proj-001")
    assert task.title == "New task"
    assert task.projectId == "proj-001"
    mock_client.mutate.assert_called_once()

def test_complete_task() -> None:
    ops, mock_client = make_mock_operations()
    task = ops.complete_task("task-001")
    assert task.isDone is True
    mock_client.mutate.assert_called_once()

def test_complete_task_not_found() -> None:
    ops, mock_client = make_mock_operations()

    def fail_mutate(
        mutator: Callable[[SpData], None],
        make_backup: bool = False,
    ) -> SpData:
        data = SpData.model_validate_json(FIXTURE_TEXT)
        del data.task.entities["task-001"]
        mutator(data)
        return data

    mock_client.mutate.side_effect = fail_mutate

    with pytest.raises(KeyError):
        ops.complete_task("task-001")

def test_update_task_title() -> None:
    ops, mock_client = make_mock_operations()
    task = ops.update_task("task-001", title="Updated title")
    assert task.title == "Updated title"
    mock_client.mutate.assert_called_once()

def test_delete_task_calls_mutate() -> None:
    ops, mock_client = make_mock_operations()
    ops.delete_task("task-001")
    mock_client.mutate.assert_called_once()

def test_list_projects() -> None:
    ops, _ = make_mock_operations()
    projects = ops.list_projects()
    assert len(projects) == 1
    assert projects[0].title == "My Project"