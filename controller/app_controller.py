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

    def fetch_and_load_station_list(self) -> bool:
        stations_json = self.service.get_station_list()
        return self.model.parse_station_list(stations_json)

    def fetch_and_load_station_data(self, station_id: str) -> bool:
        station_json = self.service.get_road_weather(station_id)
        return self.model.parse_station_data(station_json)

    def set_current_station(self, station_id: str) -> None:
        self.model.set_currect_station(station_id)

    def get_stations(self) -> list:
        return self.model.stations

    def get_current_station(self):
        return self.model.current_station
