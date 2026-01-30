from typing import Any

from model.data_model import DataModel
from .weather_service import WeatherService


class AppController:
    """Orchestrates the DataModel and WeatherService.

    Keeps business logic in one place so the UI can call simple methods
    to fetch and load data.
    """

    def __init__(self, service: WeatherService | None = None, model: DataModel | None = None) -> None:
        self.service = service or WeatherService()
        self.model = model or DataModel()
        self.last_error = ""

    def __repr__(self) -> str:
        """Return a short representation useful for debugging."""
        return f"AppController(service={self.service.__class__.__name__})"

    def fetch_and_load_station_list(self) -> bool:
        """Fetch station list via the `WeatherService` and load it into the `DataModel`.

        Returns True on successful parse and load, False if the service reported an
        error or the model failed to parse the returned data.
        """
        stations_json = self.service.get_station_list()
        if self.service.has_error:
            self.last_error = self.service.error_message
            return False
        return self.model.parse_station_list(stations_json)

    def fetch_and_load_station_data(self, station_id: str) -> bool:
        """Fetch detailed station data for `station_id` and parse it into the model.

        Returns True if parsing succeeded, False if the service reported an error
        or parsing failed.
        """
        station_json = self.service.get_road_weather(station_id)
        if self.service.has_error:
            self.last_error = self.service.error_message
            return False
        return self.model.parse_station_data(station_json)

    def set_current_station(self, station_id: str) -> None:
        """Set the currently selected station in the `DataModel` by `station_id`."""
        self.model.set_currect_station(station_id)

    def get_stations(self) -> list:
        """Return the list of parsed `WeatherStationInfo` objects from the model."""
        return self.model.stations

    def get_current_station(self):
        """Return the currently selected `WeatherStation` instance."""
        return self.model.current_station
