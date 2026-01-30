import json
import requests
from definitions import Urls


class RequestRunner:
    def __init__(self):
        self.reset_error()

    def reset_error(self):
        self.status_code = 200
        self.error_message = ""

    @property
    def has_error(self) -> bool:
        return self.status_code != 200 or self.error_message != ""

    def __execute(self, url: str, key: str = ""):
        self.reset_error()
        response = requests.Response()  # get rid of pylint warning
        try:
            response = requests.get(url)
            response.raise_for_status()
            json_data = response.json()
            if key != "":
                return json_data[key]
            else:
                return json_data
        except:
            error_json = json.loads(response.text)
            self.error_message = error_json["message"]
            return json.loads("{}")

    def get_weather_stations(self):
        """Get a list containing all weather stations from from Liikennevirasto Open Data API.
        Returns a JSON array of stations, or empty JSON on error."""

        return self.__execute(Urls.STATION_LIST_URL, "features")

    def get_road_weather(self, road_station_id):
        """Get weather data from Liikennevirasto Open Data API"""

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

        url = Urls.OPENWEATHERMAP_FORERCAST_URL.format(
            coordinates.latitude,
            coordinates.longitude,
            api_key,
        )
        return self.__execute(url)
