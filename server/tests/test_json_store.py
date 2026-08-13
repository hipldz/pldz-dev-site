import json
import multiprocessing
from pathlib import Path

import pytest

from storage.db.json_store import JsonStoreError, _read_json, _write_json


def _increment_json_counter(project_root: str, db_path: str, count: int) -> None:
    from core import ProjectConfig
    from storage.db.json_store import _lock, _read_json, _write_json

    ProjectConfig.PROJECT_ROOT = project_root
    for _ in range(count):
        with _lock:
            payload = _read_json(db_path, default={"count": 0})
            payload["count"] += 1
            _write_json(db_path, payload)


def test_json_store_rejects_corrupt_db_instead_of_returning_empty(tmp_path):
    db_path = tmp_path / "records.json"
    db_path.write_text('{"unfinished":', encoding="utf-8")

    with pytest.raises(JsonStoreError):
        _read_json(str(db_path))

    assert db_path.read_text(encoding="utf-8") == '{"unfinished":'


def test_json_store_atomically_writes_dicts_and_lists(tmp_path):
    db_path = tmp_path / "nested" / "records.json"

    _write_json(str(db_path), [{"id": "one"}])

    assert json.loads(db_path.read_text(encoding="utf-8")) == [{"id": "one"}]
    assert list(db_path.parent.glob("*.tmp")) == []


def test_json_store_lock_serializes_multiple_processes(tmp_path):
    db_path = tmp_path / "data" / "db" / "counter.json"
    processes = [
        multiprocessing.Process(
            target=_increment_json_counter,
            args=(str(tmp_path), str(db_path), 20),
        )
        for _ in range(4)
    ]

    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=10)
        assert process.exitcode == 0

    assert json.loads(db_path.read_text(encoding="utf-8"))["count"] == 80
