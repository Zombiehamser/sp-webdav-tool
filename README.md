# sp-webdav-tool

Русская версия: [README.ru.md](README.ru.md)

WebDAV client for [Super Productivity](https://super-productivity.com) — manage tasks, projects, and tags from CLI, scripts, and AI agents without running a browser.

[![Tests](https://github.com/rottentommatoe/sp-webdav-tool/actions/workflows/test.yml/badge.svg)](https://github.com/rottentommatoe/sp-webdav-tool/actions)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Overview

Super Productivity stores its synced data in `MAIN.json` and can sync it via WebDAV. This project provides a Python package and CLI to safely read and update that file without requiring a browser session, plugin bridge, or extra application server. [web:63][web:35]

## How it works

The tool connects to your WebDAV endpoint over HTTPS, downloads `MAIN.json`, reads the current ETag, applies a minimal in-memory change, and uploads the updated file back using `If-Match` for optimistic locking. This approach is designed to avoid blind overwrites when multiple Super Productivity clients sync against the same file. [web:35][web:40]

```text
Your script / Hermes agent
        │
        │  HTTPS + Basic Auth
        │  GET /webdav/MAIN.json      → read file + ETag
        │  PUT /webdav/MAIN.json      → If-Match: <etag>
        │
        ▼
your-sp-server:port/webdav/MAIN.json
        │
        │  WebDAV sync
        ▼
Desktop / mobile Super Productivity clients
```

## Requirements

- Python 3.11 or newer.
- [uv](https://docs.astral.sh/uv/) is recommended for development and installation, though `pip` also works.
- A Super Productivity setup with WebDAV sync enabled. [web:63]

## Installation

```bash
# Recommended
uv add sp-webdav-tool

# Alternative
pip install sp-webdav-tool
```

## Configuration

Copy `.env.example` to `.env` and fill in your WebDAV connection details.

```bash
cp .env.example .env
```

```env
SP_WEBDAV_URL=https://sp.example.com:51434
SP_WEBDAV_PATH=/webdav/MAIN.json
SP_WEBDAV_USERNAME=your_username
SP_WEBDAV_PASSWORD=your_password
SP_WEBDAV_TIMEOUT=10
SP_WEBDAV_RETRY_COUNT=3
```

All settings can also be provided through environment variables with the `SP_WEBDAV_` prefix.

## CLI

```bash
# List active tasks
sp-webdav tasks list

# List tasks in a specific project
sp-webdav tasks list --project <project-id>

# Add a task
sp-webdav tasks add "Deploy new version" --project <project-id>

# Mark a task as done using an ID prefix
sp-webdav tasks done a1b2c3d4

# Update task fields
sp-webdav tasks update <task-id> --title "New title"
sp-webdav tasks update <task-id> --notes "Updated notes"

# Delete a task
sp-webdav tasks delete <task-id>

# JSON output for scripting
sp-webdav tasks list --output json

# List projects
sp-webdav projects list

# Create a local backup
sp-webdav backup
```

## Python API

```python
from sp_webdav_tool import SpOperations

with SpOperations() as ops:
    tasks = ops.list_tasks()
    projects = ops.list_projects()
    tags = ops.list_tags()

    task = ops.add_task(
        "Fix bug",
        project_id="<project-id>",
        notes="See issue #42",
    )

    ops.complete_task(task.id)
    ops.update_task(task.id, title="Fixed bug", notes="Closed")
    ops.delete_task(task.id)

    backup_path = ops.backup()
```

## Hermes integration

Install the package into the Python environment used by Hermes, then register the tool definitions from `examples/hermes_config.yaml` in your Hermes configuration.

```bash
uv add sp-webdav-tool
```

After that, Hermes can call the package functions to list tasks, create tasks, update notes, complete tasks, and inspect projects without talking to a browser-based plugin bridge. The design is intended for server-side automation where only CLI access is available. [web:4][web:16]

## Safety model

- **ETag locking**: every write uses `If-Match` so stale copies do not silently overwrite newer data. [web:35][web:40]
- **Retry on conflict**: conflicting writes can be retried automatically with a small backoff.
- **Local backup support**: the current `MAIN.json` can be saved before risky operations.
- **Minimal patching**: only the required entity fields are changed instead of rebuilding the file from scratch.
- **Forward-compatible parsing**: unknown fields are preserved to reduce breakage when Super Productivity adds new fields in later versions. [web:35]

## Compatibility

This tool targets Super Productivity installations that use WebDAV sync and store data in `MAIN.json`. Since Super Productivity is local-first and sync-file-based rather than exposing a stable external server API for this workflow, compatibility should be validated against real sync files during testing. [web:63][web:35]

## Development

```bash
git clone https://github.com/rottentommatoe/sp-webdav-tool
cd sp-webdav-tool

uv sync --extra dev
uv run pytest tests/ -v
uv run ruff check src tests
uv run mypy src
```

## License

MIT