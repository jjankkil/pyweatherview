from datetime import datetime

from weatherutils import WeatherUtils


class WeatherStationInfo:
    def __init__(self):
        self._formatted_name = ""
        self._id = int(0)
        self._name = ""
        self._lat = float(0)  # location latitude
        self._lon = float(0)  # location longitude
        self._alt = float(0)  # location altitude
        self._collection_status = ""
        self._data_updated_time = datetime(1970, 1, 1, 0, 0, 0)

    def parse(self, station_json) -> bool:
        self._id = station_json["id"]
        self._name = station_json["properties"]["name"]
        self._collection_status = station_json["properties"]["collectionStatus"]
        self._lat = station_json["geometry"]["coordinates"][1]
        self._lon = station_json["geometry"]["coordinates"][0]
        self._alt = station_json["geometry"]["coordinates"][2]
        self._data_updated_time = WeatherUtils.timestamp_to_datetime(
            station_json["properties"]["dataUpdatedTime"]
        )
        return True

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def formatted_name(self) -> str:
        if self._formatted_name == "":
            self._formatted_name = WeatherUtils.format_station_name(self._name)
        return self._formatted_name


class WeatherStationList:
    def __init__(self):
        self._data_updated_time = datetime(1970, 1, 1, 0, 0, 0)
        self._features = [WeatherStationInfo()]  # list of known weather stations

    def parse(self, station_list_json) -> bool:
        self._features.clear()

        if "dataUpdatedTime" in station_list_json:
            self._data_updated_time = WeatherUtils.timestamp_to_datetime(
                station_list_json["dataUpdatedTime"]
            )

        for station_json in station_list_json["features"]:
            station = WeatherStationInfo()
            if not station.parse(station_json):
                return False
            self._features.append(station)

        return True

    def sort_by_station_name(self):
        if len(self._features) > 1:
            self._features.sort(key=lambda x: x.formatted_name)

    def find_station_id(self, formatted_name) -> int:
        station = self.find_station_by_name(formatted_name)
        return station.id

    def find_station_by_id(self, id: int) -> WeatherStationInfo:
        for station in self._features:
            if id == station.id:
                return station
        return WeatherStationInfo()

    def find_station_by_name(self, name: str) -> WeatherStationInfo:
        for station in self._features:
            if name == station.formatted_name:
                return station
        return WeatherStationInfo()

    def get_station_name_list(self):
        list = []
        for station in self._features:
            if WeatherUtils.ok_to_add_station(station.name):
                list.append(station.formatted_name)
        return list
