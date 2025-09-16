class Constants:
    SETTINGS_FILE_NAME = "settings.json"
    FORECAST_CNT = 3
    SYMBOL_CNT = FORECAST_CNT + 1
    STATION_UPDATE_DELAY_S = (
        60  # wait this many seconds more than the station's update interval
    )
    DEFAULT_POLLING_INTERVAL_S = (
        60  # if we can't determine the update interval, poll every 60s
    )


class Formats:
    SHORT_TIME_FORMAT = "%H:%M"
    TIME_FORMAT = "%H:%M:%S"
    DATE_TIME_FORMAT = "%d.%m.%Y %H:%M"
    UTC_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class Urls:
    # Open Weather Map current weather url with placeholders for city name (q) and api key (appid):
    OPENWEATHERMAP_CITY_URL = (
        "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}"
    )

    # Open Weather Map current weather url with placeholders for location (lat, lon) and api key (appid):
    OPENWEATHERMAP_LOCATION_URL = (
        "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}"
    )

    # Open Weather Map forcast url (3hrs forecasts for the next 12hrs) with placeholders for coordinates (lat, lon):
    OPENWEATHERMAP_FORERCAST_URL = (
        "https://api.openweathermap.org/data/2.5/forecast?cnt=8&lat={}&lon={}&appid={}"
    )

    # Liikennevirasto's metadata for all known weather stations:
    STATION_LIST_URL = "https://tie.digitraffic.fi/api/weather/v1/stations"

    # Liikennevirasto's weather station data with a placeholder for numeric station id, e.g. 12082:
    WEATHER_STATION_URL = "https://tie.digitraffic.fi/api/weather/v1/stations/{}/data"


class Styles:
    DEFAULT = """
        QLabel, QPushButton{
            font-family: calibri;
        }
        QLabel#station_list_label{
            font-size: 20px;
            qproperty-alignment: AlignLeft;
        }
        QComboBox#station_list{
            font-size: 18px;
        }
        QLabel#observation_time_label{
            font-size: 20px;
            qproperty-alignment: AlignLeft;
        }
        QLabel#observation_time_value{
            font-size: 20px;
            qproperty-alignment: AlignLeft;
        }
        QLabel#temperature_label{
            font-size: 20px;
            qproperty-alignment: AlignLeft;
        }
        QLabel#temperature_value{
            font-size: 20px;
            qproperty-alignment: AlignLeft;
        }
        QLabel#avg_wind_label{
            font-size: 20px;
            qproperty-alignment: AlignLeft;
        }
        QLabel#avg_wind_value{
            font-size: 20px;
            qproperty-alignment: AlignLeft;
        }
        QLabel#max_wind_label{
            font-size: 20px;
            qproperty-alignment: AlignLeft;
        }
        QLabel#max_wind_value{
            font-size: 20px;
            qproperty-alignment: AlignLeft;
        }
        QLabel#visibility_label{
            font-size: 20px;
            qproperty-alignment: AlignLeft;
        }
        QLabel#visibility_value{
            font-size: 20px;
            qproperty-alignment: AlignLeft;
        }
        QLabel#present_weather_label{
            font-size: 20px;
            qproperty-alignment: AlignLeft;
        }
        QLabel#present_weather_value{
            font-size: 20px;
            qproperty-alignment: AlignLeft;
        }
        QLabel#forecast_label{
            font-size: 20px;
            qproperty-alignment: AlignCenter;
        }
        QLabel#error_message{
            font-size: 20px;
            font-style: italic;
            qproperty-alignment: AlignCenter;
        }
        QPushButton#update_button{
            font-size: 20px;
            font-weight: bold;
        }
        QLabel#update_time_value{
            font-size: 15px;
            qproperty-alignment: AlignCenter;
        }
    """
