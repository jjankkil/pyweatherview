class Constants:
    SETTINGS_FILE_NAME = "settings.json"
    FORECAST_CNT = 3
    SYMBOL_CNT = FORECAST_CNT + 1
    STATION_UPDATE_DELAY = 120


class Formats:
    SHORT_TIME_FORMAT = "%H:%M"
    TIME_FORMAT = "%H:%M:%S"
    DATE_TIME_FORMAT = "%d.%m.%Y %H:%M"
    UTC_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class Urls:
    # Open Weather Map current weather url with placeholders for city name (q) and api key (appid):
    OPENWEATHERMAP_URL = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}"

    # Open Weather Map current weather url with placeholders for location (lat, lon) and api key (appid):
    OPENWEATHERMAP_LOCATION_URL = (
        "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}"
    )

    # Open Weather Map forcast url (3hrs forecasts for the next 12hrs) with placeholders for coordinates (lat, lon):
    FORERCAST_URL = (
        "https://api.openweathermap.org/data/2.5/forecast?cnt=8&lat={}&lon={}&appid={}"
    )

    # Liikennevirasto's metadata for all known weather stations:
    STATION_LIST_URL = "https://tie.digitraffic.fi/api/weather/v1/stations"

    # Liikennevirasto's weather station data with a placeholder for numeric station id, e.g. 12082:
    WEATHER_STATION_URL = "https://tie.digitraffic.fi/api/weather/v1/stations/{}/data"
