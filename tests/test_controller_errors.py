from controller import app_controller


class BrokenService:
    def __init__(self):
        self.has_error = True
        self.error_message = "service failure"

    def get_station_list(self):
        return {}

    def get_road_weather(self, station_id):
        return {}


def test_appcontroller_reports_service_error():
    svc = BrokenService()
    ac = app_controller.AppController(service=svc)
    ok = ac.fetch_and_load_station_list()
    assert ok is False
    assert ac.last_error == "service failure"

    ok2 = ac.fetch_and_load_station_data(1)
    assert ok2 is False
    assert ac.last_error == "service failure"
