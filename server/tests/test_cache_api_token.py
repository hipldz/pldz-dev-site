from scripts.filesystem.cache import cache_crud


def test_cache_machine_api_uploads_and_downloads(client, monkeypatch, tmp_path):
    monkeypatch.setenv("CACHE_API_TOKEN", "cache-secret")
    monkeypatch.setattr(cache_crud, "CACHE_PATH", tmp_path)
    monkeypatch.setattr(cache_crud.Logger, "info", lambda message: None)
    monkeypatch.setattr(cache_crud.Logger, "error", lambda message: None)

    url = "/api/v1/resource/cache/files/snapshot.json"
    assert client.put(url, content=b"{}", headers={"X-Cache-Token": "bad"}).status_code == 403

    upload = client.put(url, content=b"{}", headers={"X-Cache-Token": "cache-secret"})
    assert upload.status_code == 200
    assert upload.json()["data"] == {"filename": "snapshot.json", "bytes": 2}

    download = client.get(url, headers={"X-Cache-Token": "cache-secret"})
    assert download.status_code == 200
    assert download.content == b"{}"
