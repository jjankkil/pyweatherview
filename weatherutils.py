import json
import math
from datetime import datetime
from enum import Enum

import requests
from dateutil import tz

from definitions import Urls


class ConversionType(Enum):
    TO_INT = 1
    TO_FLOAT = 2


class Requestor:
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


class WeatherUtils:

    INVALID_VALUE = -999.0
    MISSING_UNIT = ["///", "???"]

    @staticmethod
    def timestamp_to_datetime(
        timestamp_str: str, is_local_time: bool = False
    ) -> datetime:
        if is_local_time:
            return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=tz.tzlocal()
            )
        return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=tz.tzutc()
        )

    @staticmethod
    def get_weather_symbol(weather_id):
        if 200 <= weather_id <= 232:
            return "⛈"
        elif 300 <= weather_id <= 321:
            return "🌦"
        elif 500 <= weather_id <= 531:
            return "🌧"
        elif 600 <= weather_id <= 622:
            return "❄"
        elif 701 <= weather_id <= 741:
            return "🌫"
        elif weather_id == 762:
            return "🌋"
        elif weather_id == 771:
            return "💨"
        elif weather_id == 781:
            return "🌪"
        elif weather_id == 800:
            return "☀"
        elif 801 <= weather_id <= 804:
            return "☁"
        else:
            return ""

    @staticmethod
    def wind_direction_as_text(degrees):
        if degrees == None:
            return ""

        while degrees > 360:
            degrees -= 360.0

        result = ""
        if (45 - 22.5) <= degrees and degrees < (45 + 22.5):
            result = "koillisesta"  # "NE"
        elif (90 - 22.5) < degrees and degrees < (90 + 22.5):
            result = "idästä"  # "E"
        elif (135 - 22.5) < degrees and degrees < (135 + 22.5):
            result = "kaakosta"  # "SE"
        elif (180 - 22.5) <= degrees and degrees < (180 + 22.5):
            result = "etelästä"  # "S"
        elif (225 - 22.5) <= degrees and degrees < (225 + 22.5):
            result = "lounaasta"  # "SW"
        elif (270 - 22.5) <= degrees and degrees < (270 + 22.5):
            result = "lännestä"  # "W"
        elif (315 - 22.5) <= degrees and degrees < (315 + 22.5):
            result = "luoteesta"  # "NW"
        else:
            result = "pohjoisesta"  # "N"

        return result

    @staticmethod
    def get_station_city(formatted_station_name) -> str:
        if formatted_station_name != None:
            if formatted_station_name.find(",") > -1:
                city = formatted_station_name.split(",")[0]
                return city

        return ""

    @staticmethod
    def format_station_name(raw_name: str):
        """Get formatted station name

        Reformats Properties.Name.FI so that city name is in the beginning.
        Example: "vt1_Espoo_Nupuri" --> "Espoo, Nupuri vt1"
        """
        if raw_name == None or raw_name == "":
            return ""

        formatted_name = ""
        tokens = raw_name.split("_")
        item_cnt = len(tokens)

        if item_cnt > 3:
            formatted_name = f"{tokens[1]}, {tokens[2]} {tokens[0]} {tokens[3]}"
        elif item_cnt == 3:
            formatted_name = f"{tokens[1]}, {tokens[2]} {tokens[0]}"
        elif item_cnt == 2:
            formatted_name = f"{tokens[1]}, {tokens[0]}"
        else:
            formatted_name = raw_name

        return formatted_name

    @staticmethod
    def ok_to_add_station(raw_name: str):
        station_name_filter_list = [
            "Test",
            "LA",
            "TSA",
            "TEST",
            "Meteo",
            "LAMID",
            "OptX",
        ]

        for filter in station_name_filter_list:
            if raw_name.find(filter) > -1:
                return False

        return True

    @staticmethod
    def __fmi_summer_simmer_index(rh: float, temp: float) -> float:
        # see https://github.com/fmidev/smartmet-library-newbase/blob/master/newbase/NFmiMetMath.cpp#L418

        simmer_limit = 14.5

        try:
            # The chart is vertical at this temperature by 0.1 degree accuracy
            if temp <= simmer_limit:
                return temp

            # When in Finland and when > 14.5 degrees, 60% is approximately the minimum mean monthly
            # humidity. However, Google wisdom claims most humans feel most comfortable either at 45%,
            # or alternatively somewhere between 50-60%. Hence we choose the middle ground 50%.
            #
            RH_REF = 50.0 / 100.0
            r = rh / 100.0
            result = (
                1.8 * temp
                - 0.55 * (1.0 - r) * (1.8 * temp - 26.0)
                - 0.55 * (1.0 - RH_REF) * 26.0
            ) / (1.8 * (1.0 - 0.55 * (1.0 - RH_REF)))
            return result

        except:
            return WeatherUtils.INVALID_VALUE

    @staticmethod
    def fmi_feels_like_temperature(wind, rh, temp) -> float:
        # see https://github.com/fmidev/smartmet-library-newbase/blob/master/newbase/NFmiMetMath.cpp#L418

        if (
            wind == WeatherUtils.INVALID_VALUE
            or rh == WeatherUtils.INVALID_VALUE
            or temp == WeatherUtils.INVALID_VALUE
        ):
            return WeatherUtils.INVALID_VALUE

        try:
            # Calculate adjusted wind chill portion. Note that even though the Canadian formula uses km/h,
            # we use m/s and have fitted the coefficients accordingly. Note that (a*w)^0.16 = c*w^16,
            # i.e. just get another coefficient c for the wind reduced to 1.5 meters.
            #
            a = 15.0  # using this the two wind chills are good match at T=0
            t0 = 37.0  # wind chill is horizontal at this T
            chill = (
                a
                + (1.0 - a / t0) * temp
                + a / t0 * math.pow(wind + 1.0, 0.16) * (temp - t0)
            )

            # Heat index
            heat = WeatherUtils.__fmi_summer_simmer_index(rh, temp)
            if heat == WeatherUtils.INVALID_VALUE:
                return WeatherUtils.INVALID_VALUE

            # Add the two corrections together
            feels_like = temp + (chill - temp) + (heat - temp)
            return feels_like

        except:
            return WeatherUtils.INVALID_VALUE
