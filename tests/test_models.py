from pathlib import Path

from sp_webdav_tool.models import SpData, Task

FIXTURE = Path(__file__).parent / "fixtures" / "main_minimal.json"

def test_parse_main_json() -> None:
    data = SpData.model_validate_json(FIXTURE.read_text(encoding="utf-8"))
    assert len(data.task.ids) == 2
    assert data.task.entities["task-001"].title == "First task"

def test_list_tasks_excludes_done() -> None:
    data = SpData.model_validate_json(FIXTURE.read_text(encoding="utf-8"))
    tasks = data.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].id == "task-001"

def test_list_tasks_filter_by_project() -> None:
    data = SpData.model_validate_json(FIXTURE.read_text(encoding="utf-8"))
    tasks = data.list_tasks(project_id="proj-001")
    assert len(tasks) == 1
    assert tasks[0].id == "task-001"

def test_list_tasks_include_done() -> None:
    data = SpData.model_validate_json(FIXTURE.read_text(encoding="utf-8"))
    tasks = data.list_tasks(include_done=True)
    assert len(tasks) == 2

def test_task_creation_defaults() -> None:
    task = Task(title="New task")
    assert task.isDone is False
    assert task.projectId == "INBOX"
    assert task.id != ""
    assert task.created > 0

def test_extra_fields_preserved() -> None:
    raw = {
        "id": "x",
        "title": "T",
        "isDone": False,
        "unknownFutureField": "v",
    }
    task = Task.model_validate(raw)
    dumped = task.model_dump()
    assert dumped["unknownFutureField"] == "v"