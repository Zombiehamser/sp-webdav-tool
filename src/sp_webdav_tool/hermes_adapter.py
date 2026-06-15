from __future__ import annotations

from sp_webdav_tool.operations import SpOperations
from sp_webdav_tool.settings import Settings

_ops: SpOperations | None = None


def get_operations() -> SpOperations:
    global _ops
    if _ops is None:
        _ops = SpOperations(Settings())  # type: ignore[call-arg]
    return _ops


def sp_list_tasks(
    project_id: str | None = None,
    include_done: bool = False,
) -> list[dict]:
    tasks = get_operations().list_tasks(project_id=project_id, include_done=include_done)
    return [
        {
            "id": task.id,
            "title": task.title,
            "isDone": task.isDone,
            "projectId": task.projectId,
            "notes": task.notes,
            "plannedAt": task.plannedAt,
            "tagIds": task.tagIds,
        }
        for task in tasks
    ]


def sp_add_task(
    title: str,
    project_id: str = "INBOX",
    notes: str = "",
    planned_at: int | None = None,
) -> dict:
    task = get_operations().add_task(
        title=title,
        project_id=project_id,
        notes=notes,
        planned_at=planned_at,
    )
    return {
        "id": task.id,
        "title": task.title,
        "projectId": task.projectId,
    }


def sp_complete_task(task_id: str) -> dict:
    task = get_operations().complete_task(task_id)
    return {
        "id": task.id,
        "title": task.title,
        "isDone": task.isDone,
    }


def sp_update_task(
    task_id: str,
    title: str | None = None,
    notes: str | None = None,
    planned_at: int | None = None,
) -> dict:
    task = get_operations().update_task(
        task_id,
        title=title,
        notes=notes,
        planned_at=planned_at,
    )
    return {
        "id": task.id,
        "title": task.title,
        "notes": task.notes,
    }


def sp_list_projects() -> list[dict]:
    projects = get_operations().list_projects()
    return [{"id": project.id, "title": project.title} for project in projects]


def sp_list_tags() -> list[dict]:
    tags = get_operations().list_tags()
    return [{"id": tag.id, "title": tag.title} for tag in tags]