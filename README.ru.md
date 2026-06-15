# sp-webdav-tool

English version: [README.md](README.md)

Python-библиотека и CLI для работы с [Super Productivity](https://super-productivity.com) через WebDAV без браузера, плагинов и дополнительных серверных прослоек.

[![Tests](https://github.com/rottentommatoe/sp-webdav-tool/actions/workflows/test.yml/badge.svg)](https://github.com/rottentommatoe/sp-webdav-tool/actions)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Описание

Super Productivity хранит синхронизируемые данные в файле `MAIN.json` и умеет работать через WebDAV. Этот проект предоставляет Python-пакет и CLI, которые безопасно читают и изменяют этот файл без запущенного браузера, без плагин-моста и без отдельного API-сервера. [web:63][web:35]

## Как это работает

Инструмент подключается к WebDAV-узлу по HTTPS, загружает `MAIN.json`, читает текущий ETag, применяет минимальное изменение в памяти и загружает обновлённый файл обратно с заголовком `If-Match` для оптимистической блокировки. Такой подход уменьшает риск слепой перезаписи, если несколько клиентов Super Productivity синхронизируются с одним и тем же файлом. [web:35][web:40]

```text
Ваш скрипт / Hermes agent
        │
        │  HTTPS + Basic Auth
        │  GET /webdav/MAIN.json      → чтение файла + ETag
        │  PUT /webdav/MAIN.json      → If-Match: <etag>
        │
        ▼
your-sp-server:port/webdav/MAIN.json
        │
        │  WebDAV sync
        ▼
Desktop / mobile Super Productivity clients
```

## Требования

- Python 3.11 или новее.
- Рекомендуется [uv](https://docs.astral.sh/uv/), но `pip` тоже поддерживается.
- Настроенный Super Productivity с включённой синхронизацией через WebDAV. [web:63]

## Установка

```bash
# Рекомендуемый вариант
uv add sp-webdav-tool

# Альтернативный вариант
pip install sp-webdav-tool
```

## Конфигурация

Скопируйте `.env.example` в `.env` и заполните параметры подключения к WebDAV.

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

Все параметры также можно передавать через переменные окружения с префиксом `SP_WEBDAV_`.

## CLI

```bash
# Показать активные задачи
sp-webdav tasks list

# Показать задачи конкретного проекта
sp-webdav tasks list --project <project-id>

# Добавить задачу
sp-webdav tasks add "Выложить новую версию" --project <project-id>

# Отметить задачу выполненной по префиксу ID
sp-webdav tasks done a1b2c3d4

# Обновить поля задачи
sp-webdav tasks update <task-id> --title "Новое название"
sp-webdav tasks update <task-id> --notes "Обновлённые заметки"

# Удалить задачу
sp-webdav tasks delete <task-id>

# Вывести данные в JSON для скриптов
sp-webdav tasks list --output json

# Показать проекты
sp-webdav projects list

# Создать локальный backup
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
        "Исправить ошибку",
        project_id="<project-id>",
        notes="См. issue #42",
    )

    ops.complete_task(task.id)
    ops.update_task(task.id, title="Ошибка исправлена", notes="Закрыто")
    ops.delete_task(task.id)

    backup_path = ops.backup()
```

## Интеграция с Hermes

Установите пакет в Python-окружение, которое использует Hermes, затем зарегистрируйте определения инструментов из `examples/hermes_config.yaml` в конфигурации Hermes.

```bash
uv add sp-webdav-tool
```

После этого Hermes сможет вызывать функции пакета для чтения списка задач, создания задач, обновления заметок, завершения задач и просмотра проектов без использования браузерного plugin bridge. Такой подход подходит для серверной автоматизации, где доступен только CLI. [web:4][web:16]

## Модель безопасности

- **ETag-блокировка**: каждая запись использует `If-Match`, чтобы устаревшая копия не перезаписала более новую версию файла. [web:35][web:40]
- **Повтор при конфликте**: конфликтующие записи можно автоматически повторять с небольшой задержкой.
- **Локальный backup**: перед рискованными операциями можно сохранить текущий `MAIN.json`.
- **Минимальные изменения**: меняются только нужные поля сущности, без полной пересборки файла с нуля.
- **Сохранение неизвестных полей**: дополнительные поля из новых версий Super Productivity сохраняются, чтобы уменьшить риск несовместимости. [web:35]

## Совместимость

Инструмент предназначен для установок Super Productivity, использующих синхронизацию через WebDAV и файл `MAIN.json`. Поскольку Super Productivity использует local-first модель и sync-файл, а не стабильный внешний серверный API для этого сценария, совместимость лучше подтверждать тестами на реальных sync-файлах. [web:63][web:35]

## Разработка

```bash
git clone https://github.com/rottentommatoe/sp-webdav-tool
cd sp-webdav-tool

uv sync --extra dev
uv run pytest tests/ -v
uv run ruff check src tests
uv run mypy src
```

## Лицензия

MIT