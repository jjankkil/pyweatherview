import math
from view.ui_helpers import get_weather_symbol as get_weather_symbol_ui
from view.ui_helpers import wind_direction_as_text as wind_direction_as_text_ui
from view.ui_helpers import get_station_city as get_station_city_ui
from view.ui_helpers import format_station_name as format_station_name_ui

from definitions import Constants


class WeatherUtils:

    # UI presentation helpers — shims forwarding to view.ui_helpers
    @staticmethod
    def get_weather_symbol(weather_id):
        return get_weather_symbol_ui(weather_id)

    @staticmethod
    def wind_direction_as_text(degrees):
        return wind_direction_as_text_ui(degrees)

    @staticmethod
    def get_station_city(formatted_station_name) -> str:
        return get_station_city_ui(formatted_station_name)

    @staticmethod
    def format_station_name(raw_name: str) -> str:
        return format_station_name_ui(raw_name)

    @staticmethod
    def fmi_feels_like_temperature(wind, rh, temp) -> float:
        # delegate pure calculation to model.physics
        try:
            from model.physics import fmi_feels_like_temperature as _f

            return _f(wind, rh, temp)
        except Exception:
            return Constants.INVALID_VALUE
