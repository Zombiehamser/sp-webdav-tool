from __future__ import annotations

import time
import uuid
from typing import Generic, TypeVar

from pydantic import BaseModel, Field


def now_ms() -> int:
    return int(time.time() * 1000)


def new_id() -> str:
    return str(uuid.uuid4())


class Task(BaseModel):
    id: str = Field(default_factory=new_id)
    title: str
    isDone: bool = False
    projectId: str = "INBOX"
    tagIds: list[str] = Field(default_factory=list)
    subTaskIds: list[str] = Field(default_factory=list)
    notes: str = ""
    timeEstimate: int = 0
    timeSpent: int = 0
    created: int = Field(default_factory=now_ms)
    plannedAt: int | None = None
    reminderId: str | None = None
    repeatCfgId: str | None = None
    parentId: str | None = None

    model_config = {"extra": "allow"}


class Project(BaseModel):
    id: str = Field(default_factory=new_id)
    title: str
    isArchived: bool = False

    model_config = {"extra": "allow"}


class Tag(BaseModel):
    id: str = Field(default_factory=new_id)
    title: str
    color: str | None = None

    model_config = {"extra": "allow"}


EntityT = TypeVar("EntityT", bound=BaseModel)


class EntityCollection(BaseModel, Generic[EntityT]):
    ids: list[str] = Field(default_factory=list)
    entities: dict[str, EntityT] = Field(default_factory=dict)


class SpData(BaseModel):
    task: EntityCollection[Task] = Field(default_factory=EntityCollection[Task])
    project: EntityCollection[Project] = Field(default_factory=EntityCollection[Project])
    tag: EntityCollection[Tag] = Field(default_factory=EntityCollection[Tag])

    model_config = {"extra": "allow"}

    def get_task(self, task_id: str) -> Task | None:
        return self.task.entities.get(task_id)

    def get_project(self, project_id: str) -> Project | None:
        return self.project.entities.get(project_id)

    def list_tasks(
        self,
        project_id: str | None = None,
        include_done: bool = False,
    ) -> list[Task]:
        tasks = list(self.task.entities.values())
        if not include_done:
            tasks = [task for task in tasks if not task.isDone]
        if project_id:
            tasks = [task for task in tasks if task.projectId == project_id]
        return tasks

    def list_projects(self) -> list[Project]:
        return list(self.project.entities.values())

    def list_tags(self) -> list[Tag]:
        return list(self.tag.entities.values())