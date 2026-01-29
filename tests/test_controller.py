from controller import app_controller


class DummyService:
    def __init__(self):
        self.has_error = False
        self.error_message = ""

    def get_station_list(self):
        # return GeoJSON-like structure expected by model.parse
        return [
            {
                "geometry": {"coordinates": [24.0, 60.0, 0.0]},
                "id": 1,
                "properties": {
                    "name": "Station 1",
                    "collectionStatus": "ON",
                    "dataUpdatedTime": "1970-01-01T00:00:00Z",
                },
            }
        ]

    def get_road_weather(self, station_id):
        return {
            "dataUpdatedTime": "1970-01-01T00:00:00Z",
            "sensorValues": [
                {
                    "id": 1,
                    "stationId": station_id,
                    "name": "ILMA",
                    "shortName": "ILMA",
                    "measuredTime": "1970-01-01T00:00:00Z",
                    "value": 10,
                    "unit": "C",
                }
            ],
        }

    def get_city_weather(self, station_id):
        return {"weather": "sunny"}

    def get_forecast(self, station_id):
        return {"list": []}


def test_appcontroller_loads_stations(monkeypatch):
    monkeypatch.setattr("controller.app_controller.WeatherService", lambda: DummyService())
    ac = app_controller.AppController()
    ok = ac.fetch_and_load_station_list()
    assert ok is True
    stations = ac.get_stations()
    assert isinstance(stations, list) and len(stations) >= 1


def test_fetch_station_data(monkeypatch):
    monkeypatch.setattr("controller.app_controller.WeatherService", lambda: DummyService())
    ac = app_controller.AppController()
    ac.fetch_and_load_station_list()
    ok = ac.fetch_and_load_station_data(1)
    assert ok is True
    current = ac.get_current_station()
    assert current is not None
