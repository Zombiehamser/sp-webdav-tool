# sp-webdav-tool

English version: [README.md](README.md)



WebDAV-клиент для [Super Productivity](https://super-productivity.com) — управление задачами, проектами и тегами из CLI, скриптов и AI-агентов без запуска браузера.

[![Tests](https://github.com/Zombiehamser/sp-webdav-tool/actions/workflows/test.yml/badge.svg)](https://github.com/Zombiehamser/sp-webdav-tool/actions)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Как это работает

Super Productivity хранит все данные в одном файле `MAIN.json` и синхронизирует его через WebDAV. Библиотека читает и записывает этот файл напрямую, используя optimistic locking через ETag.

```text
Ваш скрипт / Hermes agent
        │
        │  HTTPS + Basic Auth
        │  GET  MAIN.json  (+ ETag)
        │  PUT  MAIN.json  (If-Match: ETag)
        │
 ваш-sp-сервер:порт/webdav/MAIN.json
        │
        │  WebDAV sync
        │
 Десктоп / мобильные клиенты SP
```

## Требования

- Python 3.11+
- рекомендуется [uv](https://docs.astral.sh/uv/)
- Super Productivity с включённой WebDAV-синхронизацией

## Установка

```bash
uv sync
```

## Настройка

Создай `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Пример:

```env
SP_WEBDAV_URL=https://sp.example.com:51434
SP_WEBDAV_PATH=/webdav/MAIN.json
SP_WEBDAV_USERNAME=your_username
SP_WEBDAV_PASSWORD=your_password
```

## CLI

```bash
uv run sp-webdav tasks list
uv run sp-webdav tasks add "Проверить деплой"
uv run sp-webdav tasks done <префикс-id>
uv run sp-webdav projects list
uv run sp-webdav backup
```

## Разработка

```bash
uv sync --extra dev
uv run ruff check .
uv run mypy src tests
uv run pytest -v
```

## Лицензия

MIT