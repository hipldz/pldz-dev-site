from storage.db.json_store import _read_json, _write_json, get_deployments_db_path


class DeploymentRecordStore:
    @staticmethod
    def read() -> list[dict]:
        records = _read_json(get_deployments_db_path(), default=[])
        if not isinstance(records, list):
            raise ValueError("Deployment DB root must be an array")
        return records

    @staticmethod
    def write(records: list[dict]) -> None:
        _write_json(get_deployments_db_path(), records)
