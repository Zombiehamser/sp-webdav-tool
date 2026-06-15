# sp-webdav-tool

Русская версия: [README.ru.md](README.ru.md)



WebDAV client for [Super Productivity](https://super-productivity.com) — manage tasks, projects and tags from CLI, scripts and AI agents without running a browser.

[![Tests](https://github.com/Zombiehamser/sp-webdav-tool/actions/workflows/test.yml/badge.svg)](https://github.com/Zombiehamser/sp-webdav-tool/actions)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## How it works

Super Productivity stores all data in a single `MAIN.json` file and syncs it through WebDAV. This library reads and writes that file directly using ETag-based optimistic locking.

```text
Your script / Hermes agent
        │
        │  HTTPS + Basic Auth
        │  GET  MAIN.json  (+ ETag)
        │  PUT  MAIN.json  (If-Match: ETag)
        │
 your-sp-server:port/webdav/MAIN.json
        │
        │  WebDAV sync
        │
 Desktop / mobile SP clients
```

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