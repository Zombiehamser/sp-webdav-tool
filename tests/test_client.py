from pathlib import Path

import httpx
import pytest
import respx

from sp_webdav_tool.client import ETagConflictError, SpWebDavClient
from sp_webdav_tool.models import SpData
from sp_webdav_tool.settings import Settings

FIXTURE = Path(__file__).parent / "fixtures" / "main_minimal.json"
FIXTURE_DATA = FIXTURE.read_text(encoding="utf-8")

def make_settings() -> Settings:
    return Settings(
        url="https://sp.test:51434",
        path="/webdav/MAIN.json",
        username="user",
        password="pass",  # type: ignore[arg-type]
        timeout=10.0,
        retry_count=2,
    )

@respx.mock
def test_fetch_parses_response() -> None:
    settings = make_settings()
    route = respx.get(settings.webdav_file_url).mock(
        return_value=httpx.Response(
            200,
            text=FIXTURE_DATA,
            headers={"ETag": '"abc123"'},
        )
    )

    with SpWebDavClient(settings) as client:
        data, etag = client.fetch()

    assert route.called
    assert isinstance(data, SpData)
    assert etag == '"abc123"'
    assert len(data.task.ids) == 2

@respx.mock
def test_push_sends_if_match() -> None:
    settings = make_settings()
    route = respx.put(settings.webdav_file_url).mock(
        return_value=httpx.Response(204),
    )
    data = SpData.model_validate_json(FIXTURE_DATA)

    with SpWebDavClient(settings) as client:
        client.push(data, '"abc123"')

    assert route.called
    request = route.calls[0].request
    assert request.headers["If-Match"] == '"abc123"'

@respx.mock
def test_push_raises_on_412() -> None:
    settings = make_settings()
    respx.put(settings.webdav_file_url).mock(
        return_value=httpx.Response(412),
    )
    data = SpData.model_validate_json(FIXTURE_DATA)

    with SpWebDavClient(settings) as client, pytest.raises(ETagConflictError):
        client.push(data, '"stale"')

@respx.mock
def test_backup_writes_file(tmp_path: Path) -> None:
    settings = make_settings().model_copy(update={"backup_dir": tmp_path})
    respx.get(settings.webdav_file_url).mock(
        return_value=httpx.Response(
            200,
            text=FIXTURE_DATA,
            headers={"ETag": '"x"'},
        )
    )

    with SpWebDavClient(settings) as client:
        data, _ = client.fetch()
        path = client.backup(data)

    assert path.exists()
    assert path.name.startswith("MAIN_")