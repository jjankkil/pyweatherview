from view.background_worker import NetworkWorker


class DummyController:
    def __init__(self):
        class S:
            def __init__(self):
                self.has_error = False
                self.error_message = ""

            def get_city_weather(self, city, coordinates, api_key):
                return {"weather": "ok"}

            def get_forecast(self, coordinates, api_key):
                return {"list": []}

        self.service = S()
        # minimal model with current_station
        class C:
            formatted_name = "City, Station"
            class Coord:
                latitude = 60.0
                longitude = 24.0
            coordinates = Coord()

        self.model = type("M", (), {"current_station": C(), "stations": []})()

    def fetch_and_load_station_data(self, station_id):
        # pretend to load station data successfully
        return True


def test_network_worker_emits_finished_signal(monkeypatch):
    ctrl = DummyController()
    # instantiate worker and capture emitted values by calling run() directly
    worker = NetworkWorker(ctrl, station_id="1", api_key="key")

    results = []

    def on_finished(city, forecast, error):
        results.append((city, forecast, error))

    worker.finished.connect(on_finished)
    # call run directly (no thread) to trigger logic
    worker.run()

    assert len(results) == 1
    city, forecast, error = results[0]
    assert isinstance(city, dict)
    assert isinstance(forecast, dict)
    assert error == ""
