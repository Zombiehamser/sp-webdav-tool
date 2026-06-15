# sp-webdav-tool

Русская версия: [README.ru.md](README.ru.md)

Use [Super Productivity](https://super-productivity.com) as a scriptable task system for CLI tools, automations, and AI agents.

This project provides a small Python library and CLI for reading and updating Super Productivity data through an existing WebDAV sync target — without a browser session, without plugins, and without a third-party cloud.

[![Tests](https://github.com/Zombiehamser/sp-webdav-tool/actions/workflows/test.yml/badge.svg)](https://github.com/Zombiehamser/sp-webdav-tool/actions)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)



## Why this exists

Super Productivity is a local-first application: your data stays under your control, and sync can be handled through your own WebDAV storage. This project makes that same task data accessible to scripts, cron jobs, and server-side agents such as Hermes. 

## Why not MCP?

This project solves a different problem.

MCP-based integrations are useful when an AI assistant communicates with a running application through a dedicated bridge. This tool is designed for server-side automation and headless environments: it works directly with an existing WebDAV sync target, without a browser session, desktop UI, or plugin bridge.

Choose this project if you want:
- CLI scripts and cron automation
- server-side agents such as Hermes
- a self-hosted workflow without browser dependencies
- direct access to the same sync storage already used by your devices

## How it works

Super Productivity syncs task data through a file-based storage model. This tool reads and updates the same WebDAV sync data that your desktop and mobile clients already use.

In practice, the tool:
- downloads the current sync file,
- applies only the requested change,
- checks that the file was not changed by another client in the meantime,
- retries instead of silently overwriting newer data,
- creates backups before write operations.

## Important note

Super Productivity currently uses file-based synchronization. This tool updates the same sync data used by desktop and mobile clients, so concurrent writes from multiple devices can still create conflicts.

To reduce that risk, the library checks the file version before writing and creates automatic backups. It improves safety, but it does not replace a full conflict-free sync engine. 

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) recommended
- Super Productivity with WebDAV sync enabled

## Installation

```bash
uv sync
```

## Configuration

Create `.env` from `.env.example`:

```bash
cp .env.example .env
```

Example:

```env
SP_WEBDAV_URL=https://sp.example.com:51434
SP_WEBDAV_PATH=/webdav/MAIN.json
SP_WEBDAV_USERNAME=your_username
SP_WEBDAV_PASSWORD=your_password
```

## CLI

```bash
uv run sp-webdav tasks list
uv run sp-webdav tasks add "Deploy new version"
uv run sp-webdav tasks done <task-id-prefix>
uv run sp-webdav projects list
uv run sp-webdav backup
```

## Development

```bash
uv sync --extra dev
uv run ruff check .
uv run mypy src tests
uv run pytest -v
```

## License

MIT