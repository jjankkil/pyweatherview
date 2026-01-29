import json
from unittest.mock import patch, Mock
from utils.web_utils import RequestRunner


class DummyResponse:
    def __init__(self, status=200, json_data=None, text=""):
        self.status_code = status
        self._json = json_data or {}
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        return self._json


def test_get_weather_stations_success(monkeypatch):
    resp = DummyResponse(200, json_data={"features": [1, 2, 3]})

    def fake_get(url, timeout=None):
        return resp

    with patch("requests.get", fake_get):
        r = RequestRunner()
        out = r.get_weather_stations()
        assert isinstance(out, list) and len(out) == 3


def test_execute_handles_invalid_json(monkeypatch):
    # simulate response with invalid JSON
    resp = DummyResponse(200, json_data=None, text="notjson")

    def fake_get(url, timeout=None):
        # return object whose json() will raise ValueError
        m = Mock()
        m.status_code = 200
        m.text = "notjson"

        def raise_for_status():
            return None

        def json_raiser():
            raise ValueError("No JSON")

        m.raise_for_status = raise_for_status
        m.json = json_raiser
        return m

    with patch("requests.get", fake_get):
        r = RequestRunner()
        out = r.get_weather_stations()
        # should return empty-ish structure (list or dict)
        assert out == {}
