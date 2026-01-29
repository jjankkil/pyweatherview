from PyQt6.QtCore import QThread, pyqtSignal
from typing import Any


class NetworkWorker(QThread):
    """Background worker to perform network calls without blocking the UI.

    Emits a `finished` signal with (city_data, forecast, error_message).
    """

    finished = pyqtSignal(object, object, str)

    def __init__(self, controller, station_id: str, api_key: str):
        super().__init__()
        self.controller = controller
        self.station_id = station_id
        self.api_key = api_key

    def run(self) -> None:
        try:
            # Fetch and parse road weather into the model
            success = self.controller.fetch_and_load_station_data(self.station_id)
            if self.controller.service.has_error:
                err = self.controller.service.error_message
                self.finished.emit({}, {}, err)
                return

            # Get city weather and forecast (may return empty dicts on error)
            city = self.controller.service.get_city_weather(
                self.controller.model.current_station.formatted_name,
                self.controller.model.current_station.coordinates,
                self.api_key,
            )
            if self.controller.service.has_error:
                err = self.controller.service.error_message
                # still emit city and empty forecast so UI can update what it has
                self.finished.emit(city or {}, {}, err)
                return

            forecast = self.controller.service.get_forecast(
                self.controller.model.current_station.coordinates, self.api_key
            )
            if self.controller.service.has_error:
                err = self.controller.service.error_message
                self.finished.emit(city or {}, forecast or {}, err)
                return

            # Success
            self.finished.emit(city or {}, forecast or {}, "")

        except Exception as exc:
            self.finished.emit({}, {}, str(exc))
