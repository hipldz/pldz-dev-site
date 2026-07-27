import asyncio

import pytest

from scripts.filesystem.cache import cache_crud


def test_cache_stream_is_atomic_and_rejects_path_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_crud, "CACHE_PATH", tmp_path)
    monkeypatch.setattr(cache_crud.Logger, "info", lambda message: None)
    monkeypatch.setattr(cache_crud.Logger, "error", lambda message: None)
    cache_crud.CacheCrudHandle.save_cache_file("existing.txt", b"old")

    async def oversized_stream():
        yield b"x" * 11

    with pytest.raises(ValueError, match="exceeds"):
        asyncio.run(
            cache_crud.CacheCrudHandle.save_cache_stream(
                "existing.txt", oversized_stream(), max_bytes=10
            )
        )

    assert (tmp_path / "existing.txt").read_bytes() == b"old"
    assert cache_crud.CacheCrudHandle.get_cache_file("../outside.txt") == ""


def test_cache_stream_replaces_file_after_complete_upload(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_crud, "CACHE_PATH", tmp_path)
    monkeypatch.setattr(cache_crud.Logger, "info", lambda message: None)

    async def chunks():
        yield b"hello "
        yield b"world"

    written = asyncio.run(
        cache_crud.CacheCrudHandle.save_cache_stream(
            "snapshot.txt", chunks(), content_length=11
        )
    )

    assert written == 11
    assert (tmp_path / "snapshot.txt").read_bytes() == b"hello world"
