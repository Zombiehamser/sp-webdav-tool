from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import time

import httpx

from sp_webdav_tool.models import SpData
from sp_webdav_tool.settings import Settings


class ETagConflictError(Exception):
    pass


class SpWebDavClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.http = httpx.Client(
            auth=(settings.username, settings.password.get_secret_value()),
            timeout=settings.timeout,
            verify=True,
        )

    def close(self) -> None:
        self.http.close()

    def __enter__(self) -> SpWebDavClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def fetch(self) -> tuple[SpData, str]:
        response = self.http.get(self.settings.webdav_file_url)
        response.raise_for_status()
        etag = response.headers.get("ETag", "")
        return SpData.model_validate(response.json()), etag

    def push(self, data: SpData, etag: str) -> None:
        headers = {"Content-Type": "application/json"}
        if etag:
            headers["If-Match"] = etag

        response = self.http.put(
            self.settings.webdav_file_url,
            content=data.model_dump_json(exclude_none=False),
            headers=headers,
        )

        if response.status_code == 412:
            raise ETagConflictError("WebDAV file changed during update")

        response.raise_for_status()

    def backup(self, data: SpData) -> Path:
        backup_dir = self.settings.backup_dir
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"MAIN_{int(time.time())}.json"
        backup_path.write_text(data.model_dump_json(indent=2), encoding="utf-8")
        return backup_path

    def mutate(
        self,
        mutator: Callable[[SpData], None],
        *,
        make_backup: bool = False,
    ) -> SpData:
        last_error: Exception | None = None

        for attempt in range(self.settings.retry_count):
            data, etag = self.fetch()

            if make_backup and attempt == 0:
                self.backup(data)

            mutator(data)

            try:
                self.push(data, etag)
                return data
            except ETagConflictError as exc:
                last_error = exc
                time.sleep(0.4 * (attempt + 1))

        raise ETagConflictError(
            f"Failed to update MAIN.json after {self.settings.retry_count} attempts"
        ) from last_error