from typing import Any

from utils.web_utils import RequestRunner


class WeatherService:
    """Thin wrapper around the existing RequestRunner to provide a
    clearer service interface for the rest of the application.
    """

    def __init__(self) -> None:
        self._runner = RequestRunner()

    @property
    def has_error(self) -> bool:
        return self._runner.has_error

    @property
    def error_message(self) -> str:
        return self._runner.error_message

    def get_station_list(self) -> Any:
        return self._runner.get_weather_stations()

    def get_road_weather(self, station_id: str) -> Any:
        return self._runner.get_road_weather(station_id)

    def get_city_weather(self, city: str, coordinates, api_key: str) -> Any:
        return self._runner.get_city_weather(city, coordinates, api_key)

    def get_forecast(self, coordinates, api_key: str) -> Any:
        return self._runner.get_forecast(coordinates, api_key)
