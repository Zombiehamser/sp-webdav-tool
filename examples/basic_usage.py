from sp_webdav_tool import SpOperations

with SpOperations() as ops:
    projects = ops.list_projects()
    for p in projects:
        print(p.id[:8], p.title)

    tasks = ops.list_tasks()
    for t in tasks:
        print(t.id[:8], t.title)

    new_task = ops.add_task(
        title="Review deployment",
        project_id=projects[0].id if projects else "INBOX",
        notes="Check docker logs after release",
    )
    print("Created:", new_task.id)

    ops.complete_task(new_task.id)
    print("Done.")