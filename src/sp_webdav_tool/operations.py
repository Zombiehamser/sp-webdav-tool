from __future__ import annotations

from pathlib import Path

from sp_webdav_tool.client import SpWebDavClient
from sp_webdav_tool.models import Project, SpData, Tag, Task
from sp_webdav_tool.settings import Settings


class SpOperations:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()  # type: ignore[call-arg]
        self.client = SpWebDavClient(self.settings)

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> SpOperations:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def list_tasks(
        self,
        project_id: str | None = None,
        include_done: bool = False,
    ) -> list[Task]:
        data, _ = self.client.fetch()
        return data.list_tasks(project_id=project_id, include_done=include_done)

    def get_task(self, task_id: str) -> Task | None:
        data, _ = self.client.fetch()
        return data.get_task(task_id)

    def list_projects(self) -> list[Project]:
        data, _ = self.client.fetch()
        return data.list_projects()

    def list_tags(self) -> list[Tag]:
        data, _ = self.client.fetch()
        return data.list_tags()

    def add_task(
        self,
        title: str,
        project_id: str = "INBOX",
        notes: str = "",
        planned_at: int | None = None,
        tag_ids: list[str] | None = None,
    ) -> Task:
        task = Task(
            title=title,
            projectId=project_id,
            notes=notes,
            plannedAt=planned_at,
            tagIds=tag_ids or [],
        )

        def mutator(data: SpData) -> None:
            data.task.entities[task.id] = task
            if task.id not in data.task.ids:
                data.task.ids.append(task.id)

        self.client.mutate(mutator, make_backup=True)
        return task

    def update_task(
        self,
        task_id: str,
        title: str | None = None,
        notes: str | None = None,
        planned_at: int | None = None,
        project_id: str | None = None,
    ) -> Task:
        updated_task: Task | None = None

        def mutator(data: SpData) -> None:
            nonlocal updated_task
            task = data.task.entities.get(task_id)
            if task is None:
                raise KeyError(f"Task not found: {task_id}")
            if title is not None:
                task.title = title
            if notes is not None:
                task.notes = notes
            if planned_at is not None:
                task.plannedAt = planned_at
            if project_id is not None:
                task.projectId = project_id
            updated_task = task

        self.client.mutate(mutator, make_backup=True)
        if updated_task is None:
            raise KeyError(f"Task not found: {task_id}")
        return updated_task

    def complete_task(self, task_id: str) -> Task:
        completed_task: Task | None = None

        def mutator(data: SpData) -> None:
            nonlocal completed_task
            task = data.task.entities.get(task_id)
            if task is None:
                raise KeyError(f"Task not found: {task_id}")
            task.isDone = True
            completed_task = task

        self.client.mutate(mutator, make_backup=True)
        if completed_task is None:
            raise KeyError(f"Task not found: {task_id}")
        return completed_task

    def delete_task(self, task_id: str) -> None:
        def mutator(data: SpData) -> None:
            if task_id not in data.task.entities:
                raise KeyError(f"Task not found: {task_id}")
            del data.task.entities[task_id]
            data.task.ids = [item_id for item_id in data.task.ids if item_id != task_id]

        self.client.mutate(mutator, make_backup=True)

    def add_project(self, title: str) -> Project:
        project = Project(title=title)

        def mutator(data: SpData) -> None:
            data.project.entities[project.id] = project
            if project.id not in data.project.ids:
                data.project.ids.append(project.id)

        self.client.mutate(mutator, make_backup=True)
        return project

    def backup(self) -> Path:
        data, _ = self.client.fetch()
        return self.client.backup(data)