from enum import Enum

OPENWEATHERMAP_API_KEY = "your_own_open_weather_api_key_here"

# Open Weather Map current weather url with placeholders for city name (q) and api key (appid):
OPENWEATHERMAP_URL = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}"

# Open Weather Map forecast url with placeholders for coordinates (lat, lon):
FORERCAST_URL = "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=current,minutely,hourly,alerts&appid={}"

# Liikennevirasto's metadata for all known weather stations:
STATION_LIST_URL = "https://tie.digitraffic.fi/api/weather/v1/stations"

# Liikennevirasto's weather station data with a placeholder for numeric station id, e.g. 12082:
WEATHER_STATION_URL = "https://tie.digitraffic.fi/api/weather/v1/stations/{}/data"


class ConversionType(Enum):
    TO_INT = 1
    TO_FLOAT = 2
