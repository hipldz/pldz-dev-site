import asyncio

import pytest

from storage.cache.operations import files as cache_files


def test_cache_stream_is_atomic_and_rejects_path_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_files, "CACHE_PATH", tmp_path)
    monkeypatch.setattr(cache_files.Logger, "info", lambda message: None)
    monkeypatch.setattr(cache_files.Logger, "error", lambda message: None)
    cache_files.CacheStore.save_cache_file("existing.txt", b"old")

    async def oversized_stream():
        yield b"x" * 11

    with pytest.raises(ValueError, match="exceeds"):
        asyncio.run(
            cache_files.CacheStore.save_cache_stream(
                "existing.txt", oversized_stream(), max_bytes=10
            )
        )

    assert (tmp_path / "existing.txt").read_bytes() == b"old"
    assert cache_files.CacheStore.get_cache_file("../outside.txt") == ""


def test_cache_stream_replaces_file_after_complete_upload(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_files, "CACHE_PATH", tmp_path)
    monkeypatch.setattr(cache_files.Logger, "info", lambda message: None)

    async def chunks():
        yield b"hello "
        yield b"world"

    written = asyncio.run(
        cache_files.CacheStore.save_cache_stream(
            "snapshot.txt", chunks(), content_length=11
        )
    )

    assert written == 11
    assert (tmp_path / "snapshot.txt").read_bytes() == b"hello world"


def test_cache_catalog_lists_nested_files(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_files, "CACHE_PATH", tmp_path)
    nested = tmp_path / "llm" / "result.json"
    nested.parent.mkdir(parents=True)
    nested.write_text("{}", encoding="utf-8")

    files = cache_files.CacheStore.get_all_cache_files()

    assert files[0]["filename"] == "llm/result.json"
    assert files[0]["category"] == "llm"
    assert cache_files.CacheStore.get_cache_file("llm/result.json") == str(nested)
