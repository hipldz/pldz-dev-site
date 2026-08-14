from storage.resource.files import ResourceFileStore


def test_resource_catalog_lists_nested_files(tmp_path, monkeypatch):
    from core import ProjectConfig

    monkeypatch.setattr(ProjectConfig, "get_resource_path", classmethod(lambda cls: str(tmp_path)))
    nested = tmp_path / "llm" / "models.json"
    nested.parent.mkdir(parents=True)
    nested.write_text("{}", encoding="utf-8")

    files = ResourceFileStore.list_files()

    assert files == [{
        "path": "llm/models.json",
        "category": "llm",
        "filename": "models.json",
        "modified_time": nested.stat().st_mtime,
        "size": 2,
    }]
