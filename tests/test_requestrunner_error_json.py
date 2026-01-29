from utils.web_utils import RequestRunner
from unittest.mock import Mock, patch
import requests


def test_requestrunner_extracts_error_message_from_json():
    m = Mock()
    m.status_code = 500
    m.raise_for_status.side_effect = requests.HTTPError("500")
    m.json.return_value = {"message": "internal error"}

    def fake_get(url, timeout=None):
        return m

    with patch("requests.get", fake_get):
        r = RequestRunner()
        out = r.get_road_weather(1)
        assert out == {}
        assert r.status_code == 500
        assert r.error_message == "internal error"
