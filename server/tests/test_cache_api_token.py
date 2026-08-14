from storage.cache.operations import files as cache_files


def test_cache_machine_api_uploads_and_downloads(client, monkeypatch, tmp_path):
    monkeypatch.setenv("CACHE_API_TOKEN", "cache-secret")
    monkeypatch.setattr(cache_files, "CACHE_PATH", tmp_path)
    monkeypatch.setattr(cache_files.Logger, "info", lambda message: None)
    monkeypatch.setattr(cache_files.Logger, "error", lambda message: None)

    url = "/api/v1/cache/files/snapshot.json"
    assert client.put(url, content=b"{}", headers={"X-Cache-Token": "bad"}).status_code == 403

    upload = client.put(url, content=b"{}", headers={"X-Cache-Token": "cache-secret"})
    assert upload.status_code == 200
    assert upload.json()["data"] == {"filename": "snapshot.json", "bytes": 2}

    download = client.get(url, headers={"X-Cache-Token": "cache-secret"})
    assert download.status_code == 200
    assert download.content == b"{}"

    public_file = tmp_path / "llm" / "result.json"
    public_file.parent.mkdir()
    public_file.write_bytes(b'{"ok": true}')
    public_download = client.get("/api/v1/cache/llm/result.json")
    assert public_download.status_code == 200
    assert public_download.content == b'{"ok": true}'
