from view.background_worker import NetworkWorker


class ErrService:
    def __init__(self):
        self.has_error = True
        self.error_message = "service fail"

    def get_city_weather(self, *args, **kwargs):
        return {}

    def get_forecast(self, *args, **kwargs):
        return {}


class ErrController:
    def __init__(self):
        self.service = ErrService()

        class C:
            formatted_name = "City"
            class Coord:
                latitude = 60.0
                longitude = 24.0
            coordinates = Coord()

        self.model = type("M", (), {"current_station": C()})()

    def fetch_and_load_station_data(self, station_id):
        # pretend that loading fails and service reports error
        return False


def test_network_worker_emits_error(monkeypatch):
    ctrl = ErrController()
    worker = NetworkWorker(ctrl, station_id="1", api_key="key")
    results = []

    def on_finished(city, forecast, error):
        results.append((city, forecast, error))

    worker.finished.connect(on_finished)
    worker.run()

    assert len(results) == 1
    city, forecast, error = results[0]
    assert city == {}
    assert forecast == {}
    assert error == "service fail"
