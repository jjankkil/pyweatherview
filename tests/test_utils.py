import os
import json
import tempfile
from utils.utils import Utils
from datetime import datetime, timezone


def test_timestamp_to_datetime_utc_local():
    ts = "2020-01-01T12:00:00Z"
    dt_utc = Utils.timestamp_to_datetime(ts, is_local_time=False)
    assert dt_utc.tzinfo is not None


def test_load_and_save_settings(tmp_path):
    f = tmp_path / "test_settings.json"
    data = {"openweathermap_api_key": "abc"}
    Utils.save_settings(str(f), data)
    loaded = Utils.load_settings(str(f))
    assert loaded["openweathermap_api_key"] == "abc"


def test_calculate_seconds_until_next_update():
    now = datetime.now(timezone.utc).timestamp()
    latest = now - 60
    previous = now - 120
    s = Utils.calculate_seconds_until_next_update(latest, previous)
    assert isinstance(s, (int, float))
