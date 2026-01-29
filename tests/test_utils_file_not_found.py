from utils.utils import Utils
import os


def test_load_settings_missing_file(tmp_path):
    p = tmp_path / "no_such_file.json"
    # ensure file does not exist
    if p.exists():
        p.unlink()
    settings = Utils.load_settings(str(p))
    # defaults should be present
    assert isinstance(settings, dict)
    assert settings.get("openweathermap_api_key", "") == ""
    assert isinstance(settings.get("latest_stations", []), list)
