from sp_webdav_tool import SpOperations


def main() -> None:
    with SpOperations() as ops:
        projects = ops.list_projects()
        for project in projects:
            print(project.id[:8], project.title)

        tasks = ops.list_tasks()
        for task in tasks:
            print(task.id[:8], task.title)

        new_task = ops.add_task(
            title="Review deployment",
            project_id=projects[0].id if projects else "INBOX",
            notes="Check docker logs after release",
        )
        print("Created:", new_task.id)

        completed = ops.complete_task(new_task.id)
        print("Completed:", completed.id)


if __name__ == "__main__":
    main()