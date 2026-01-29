from controller.weather_service import WeatherService


class DummyRunner:
    def __init__(self):
        self.has_error = False
        self.error_message = ""

    def get_weather_stations(self):
        return ["s1", "s2"]

    def get_road_weather(self, station_id):
        return {"dataUpdatedTime": "1970-01-01T00:00:00Z", "sensorValues": []}

    def get_city_weather(self, city, coordinates, api_key):
        return {"weather": "ok"}

    def get_forecast(self, coordinates, api_key):
        return {"list": []}


def test_weather_service_methods(monkeypatch):
    monkeypatch.setattr("controller.weather_service.RequestRunner", lambda: DummyRunner())
    svc = WeatherService()
    assert svc.get_station_list() == ["s1", "s2"]
    assert svc.get_road_weather(1)["sensorValues"] == []
    assert svc.get_city_weather("Helsinki", (60.17, 24.94), "key")["weather"] == "ok"
    assert isinstance(svc.get_forecast((60.17, 24.94), "key"), dict)
