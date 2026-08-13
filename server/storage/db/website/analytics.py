from storage.db.json_store import _read_json, _write_json, get_analytics_db_path


class AnalyticsRecordStore:
    @staticmethod
    def read() -> dict:
        data = _read_json(
            get_analytics_db_path(),
            default={"daily": {}, "recent_events": []},
        )
        if not isinstance(data, dict):
            raise ValueError("Analytics DB root must be an object")
        data.setdefault("daily", {})
        data.setdefault("recent_events", [])
        return data

    @staticmethod
    def write(data: dict) -> None:
        _write_json(get_analytics_db_path(), data)
