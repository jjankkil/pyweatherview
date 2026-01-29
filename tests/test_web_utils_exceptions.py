import requests
from utils.web_utils import RequestRunner
from requests.exceptions import RequestException
from unittest.mock import patch


def test_requests_get_raises_request_exception():
    def fake_get(url, timeout=None):
        raise RequestException("network down")

    with patch("requests.get", fake_get):
        r = RequestRunner()
        out = r.get_weather_stations()
        assert out == {}
        assert r.status_code == 0
        assert r.has_error
