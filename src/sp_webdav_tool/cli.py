from __future__ import annotations

import json
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from sp_webdav_tool.operations import SpOperations
from sp_webdav_tool.settings import Settings

app = typer.Typer(name="sp-webdav", help="Super Productivity WebDAV CLI")
tasks_app = typer.Typer(help="Manage tasks")
projects_app = typer.Typer(help="Manage projects")

app.add_typer(tasks_app, name="tasks")
app.add_typer(projects_app, name="projects")

console = Console()


def get_operations() -> SpOperations:
    return SpOperations(Settings())  # type: ignore[call-arg]


@tasks_app.command("list")
def tasks_list(
    project: Annotated[str | None, typer.Option("--project", "-p")] = None,
    done: Annotated[bool, typer.Option("--done")] = False,
    output: Annotated[str, typer.Option("--output", "-o")] = "table",
) -> None:
    with get_operations() as ops:
        tasks = ops.list_tasks(project_id=project, include_done=done)

    if output == "json":
        console.print_json(json.dumps([task.model_dump() for task in tasks]))
        return

    table = Table(title="Tasks", show_lines=False)
    table.add_column("ID", style="dim", no_wrap=True, max_width=8)
    table.add_column("Title")
    table.add_column("Project", style="cyan")
    table.add_column("Done", justify="center")

    for task in tasks:
        table.add_row(
            task.id[:8],
            task.title,
            task.projectId or "—",
            "✓" if task.isDone else "",
        )

    console.print(table)


@tasks_app.command("add")
def tasks_add(
    title: Annotated[str, typer.Argument(help="Task title")],
    project: Annotated[str, typer.Option("--project", "-p")] = "INBOX",
    notes: Annotated[str, typer.Option("--notes", "-n")] = "",
) -> None:
    with get_operations() as ops:
        task = ops.add_task(title=title, project_id=project, notes=notes)

    console.print(
        f"[green]✓[/green] Created task [bold]{task.id[:8]}[/bold]: {task.title}"
    )


@tasks_app.command("done")
def tasks_done(
    task_id: Annotated[str, typer.Argument(help="Task ID or prefix")],
) -> None:
    with get_operations() as ops:
        tasks = ops.list_tasks(include_done=True)
        matched = [task for task in tasks if task.id.startswith(task_id)]

        if not matched:
            console.print(f"[red]Task not found:[/red] {task_id}")
            raise typer.Exit(1)

        if len(matched) > 1:
            console.print(
                f"[red]Ambiguous prefix:[/red] {task_id} matches {len(matched)} tasks"
            )
            raise typer.Exit(1)

        task = ops.complete_task(matched[0].id)

    console.print(f"[green]✓[/green] Completed: {task.title}")


@tasks_app.command("update")
def tasks_update(
    task_id: Annotated[str, typer.Argument()],
    title: Annotated[str | None, typer.Option("--title")] = None,
    notes: Annotated[str | None, typer.Option("--notes")] = None,
) -> None:
    with get_operations() as ops:
        task = ops.update_task(task_id, title=title, notes=notes)

    console.print(f"[green]✓[/green] Updated: {task.title}")


@tasks_app.command("delete")
def tasks_delete(
    task_id: Annotated[str, typer.Argument()],
    yes: Annotated[bool, typer.Option("--yes", "-y")] = False,
) -> None:
    if not yes:
        typer.confirm(f"Delete task {task_id}?", abort=True)

    with get_operations() as ops:
        ops.delete_task(task_id)

    console.print(f"[green]✓[/green] Deleted task {task_id}")


@projects_app.command("list")
def projects_list(
    output: Annotated[str, typer.Option("--output", "-o")] = "table",
) -> None:
    with get_operations() as ops:
        projects = ops.list_projects()

    if output == "json":
        console.print_json(json.dumps([project.model_dump() for project in projects]))
        return

    table = Table(title="Projects")
    table.add_column("ID", style="dim", no_wrap=True, max_width=8)
    table.add_column("Title")
    table.add_column("Archived", justify="center")

    for project in projects:
        table.add_row(
            project.id[:8],
            project.title,
            "✓" if project.isArchived else "",
        )

    console.print(table)


@projects_app.command("add")
def projects_add(
    title: Annotated[str, typer.Argument()],
) -> None:
    with get_operations() as ops:
        project = ops.add_project(title)

    console.print(
        f"[green]✓[/green] Created project [bold]{project.id[:8]}[/bold]: {project.title}"
    )


@app.command("backup")
def backup_command() -> None:
    with get_operations() as ops:
        path = ops.backup()

    console.print(f"[green]✓[/green] Backup saved: {path}")