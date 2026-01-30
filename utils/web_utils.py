import json
import requests
from requests.exceptions import RequestException
from definitions import Urls


class RequestRunner:
    def __init__(self):
        """Create a RequestRunner and initialize error state.

        This object provides safe GET requests with JSON parsing and error
        extraction helpers used across the application.
        """
        self.reset_error()

    def reset_error(self):
        # 200 means OK; 0 means no response (network failure)
        self.status_code = 200
        self.error_message = ""

    @property
    def has_error(self) -> bool:
        """True when the last executed request ended in an error.

        An error is signaled either by a non-200 HTTP status or a non-empty
        `error_message` parsed from the response or exception.
        """
        return self.status_code != 200 or self.error_message != ""

    def __execute(self, url: str, key: str = ""):
        """Execute a GET request and return parsed JSON or an empty dict on error.

        This method sets `self.status_code` and `self.error_message` so callers
        can decide how to surface problems to the user.
        """
        self.reset_error()
        response = None
        try:
            response = requests.get(url, timeout=10)
            # raise HTTPError on 4xx/5xx
            response.raise_for_status()
            try:
                json_data = response.json()
            except ValueError:
                # Invalid JSON body
                self.status_code = response.status_code if response is not None else 0
                self.error_message = "Invalid JSON response"
                return {}

            if key:
                return json_data.get(key, {})
            return json_data

        except RequestException as exc:
            # Network-level error or non-2xx status
            if response is not None:
                # try to extract a message from the response body, fall back to exception text
                try:
                    err = response.json()
                    self.error_message = err.get("message", str(exc))
                except Exception:
                    self.error_message = str(exc)
                self.status_code = response.status_code
            else:
                self.status_code = 0
                self.error_message = str(exc)

            return {}

    def get_weather_stations(self):
        """Get a list containing all weather stations from from Liikennevirasto Open Data API.
        Returns a JSON array of stations, or empty JSON on error."""

        """Fetch the list of weather stations and return the `features` array.

        Returns an empty structure on error and sets `status_code`/`error_message`.
        """
        return self.__execute(Urls.STATION_LIST_URL, "features")

    def get_road_weather(self, road_station_id):
        """Get weather data from Liikennevirasto Open Data API"""

        """Fetch detailed road weather JSON for the `road_station_id`."""
        url = Urls.WEATHER_STATION_URL.format(road_station_id)
        return self.__execute(url)

    def get_city_weather(self, city: str, coordinates, api_key: str):
        """Get weather data from Open Weathermap API.
        This is needed for the present weather symbol."""

        url = Urls.OPENWEATHERMAP_CITY_URL.format(city, api_key)
        data = self.__execute(url)
        if self.has_error:
            # failed to get weather by city name, try again with coordinates:
            url = Urls.OPENWEATHERMAP_LOCATION_URL.format(
                coordinates.latitude,
                coordinates.longitude,
                api_key,
            )
            data = self.__execute(url)

        return data

    def get_forecast(self, coordinates, api_key: str):
        """Get weather forecast from Open Weathermap API"""

        """Fetch forecast JSON for `coordinates` using OpenWeatherMap."""
        url = Urls.OPENWEATHERMAP_FORERCAST_URL.format(
            coordinates.latitude,
            coordinates.longitude,
            api_key,
        )
        return self.__execute(url)
