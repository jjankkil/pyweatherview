from datetime import datetime

from .helpers import ok_to_add_station
from utils.utils import Utils
from utils.weather_utils import WeatherUtils


class WeatherStationInfo:
    class Coordinates:
        def __init__(self, lat=0.0, lon=0.0, alt=0.0):
            self._lat = lat  # location latitude
            self._lon = lon  # location longitude
            self._alt = alt  # location altitude

        @property
        def latitude(self):
            return self._lat

        @property
        def longitude(self):
            return self._lon

        @property
        def altitude(self):
            return self._alt

    class Properties:
        def __init__(self):
            self._id = int(0)
            self._name = ""
            self._collection_status = ""
            self._data_updated_time = datetime(1970, 1, 1, 0, 0, 0)

    def __init__(self):
        self._formatted_name = ""
        self._coordinates = WeatherStationInfo.Coordinates()
        self._properties = WeatherStationInfo.Properties()

    def parse(self, station_json) -> bool:
        """Parse a single station JSON object into this `WeatherStationInfo`.

        The expected input follows the Digitraffic station schema (geometry + properties).
        Returns True on success, False on failure.
        """
        self._coordinates._lat = station_json["geometry"]["coordinates"][1]
        self._coordinates._lon = station_json["geometry"]["coordinates"][0]
        self._coordinates._alt = station_json["geometry"]["coordinates"][2]
        self._properties._id = station_json["id"]
        self._properties._name = station_json["properties"]["name"]
        self._properties._collection_status = station_json["properties"][
            "collectionStatus"
        ]
        self._properties._data_updated_time = Utils.timestamp_to_datetime(
            station_json["properties"]["dataUpdatedTime"]
        )
        return True

    @property
    def id(self) -> int:
        """Station identifier as an integer parsed from source JSON."""
        return self._properties._id

    @property
    def name(self) -> str:
        """Raw station name string (as provided by the station metadata)."""
        return self._properties._name

    @property
    def formatted_name(self) -> str:
        """Return a human-friendly formatted station name (cached)."""
        if self._formatted_name == "":
            self._formatted_name = WeatherUtils.format_station_name(
                self._properties._name
            )
        return self._formatted_name

    @property
    def coordinates(self):
        return self._coordinates


class WeatherStationList:
    def __init__(self):
        # self._data_updated_time = datetime(1970, 1, 1, 0, 0, 0)
        self._stations = [WeatherStationInfo()]  # list of known weather stations

    def parse(self, station_list_json) -> bool:
        self._stations.clear()

        for station_json in station_list_json:
            station_info = WeatherStationInfo()
            if not station_info.parse(station_json):
                return False
            self._stations.append(station_info)

        return True

    @property
    def stations(self):
        return self._stations

    def sort_by_station_name(self):
        if len(self._stations) > 1:
            self._stations.sort(key=lambda x: x.formatted_name)

    def find_station_id(self, formatted_name) -> int:
        station = self.find_station_by_name(formatted_name)
        return station.id

    def find_station_by_id(self, id: int) -> WeatherStationInfo:
        for station in self._stations:
            if id == station.id:
                return station
        return WeatherStationInfo()

    def find_station_by_name(self, name: str) -> WeatherStationInfo:
        for station in self._stations:
            if name == station.formatted_name:
                return station
        return WeatherStationInfo()

    def get_station_name_list(self):
        list = []
        for station in self._stations:
            if ok_to_add_station(station.name):
                list.append(station.formatted_name)
        return list
