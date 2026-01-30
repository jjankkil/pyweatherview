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
        """True when the underlying request runner has recorded an error."""
        return self._runner.has_error

    @property
    def error_message(self) -> str:
        """Return last error message from the underlying request runner."""
        return self._runner.error_message

    def get_station_list(self) -> Any:
        """Return the raw station list JSON from the network runner.

        The returned structure is forwarded unchanged to the caller (usually
        `AppController`) which is responsible for parsing it into model objects.
        """
        return self._runner.get_weather_stations()

    def get_road_weather(self, station_id: str) -> Any:
        """Return detailed road/weather data for the given `station_id`."""
        return self._runner.get_road_weather(station_id)

    def get_city_weather(self, city: str, coordinates, api_key: str) -> Any:
        """Get current weather for a city (or fallback to coordinates).

        Returns the JSON response from the OpenWeatherMap endpoint.
        """
        return self._runner.get_city_weather(city, coordinates, api_key)

    def get_forecast(self, coordinates, api_key: str) -> Any:
        """Return forecast JSON for the given coordinates.

        The result is used to display short-term forecasts in the UI.
        """
        return self._runner.get_forecast(coordinates, api_key)
