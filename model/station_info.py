from datetime import datetime

from weatherutils import WeatherUtils


class WeatherStation:
    def __init__(self):
        self._formatted_name = ""
        self._id = int(0)
        self._name = ""

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
        self._type = ""
        self._data_updated_time = datetime(1970, 1, 1, 0, 0, 0)
        self._features = [WeatherStation()]  # list of known weather stations

    def sort_by_station_name(self):
        if len(self._features) > 1:
            self._features.sort(key=lambda x: x.formatted_name)

    def find_station_id(self, formatted_name) -> int:
        station = self.find_station_by_name(formatted_name)
        return station.id

    def find_station_by_id(self, id: int) -> WeatherStation:
        for station in self._features:
            if id == station.id:
                return station
        return WeatherStation()

    def find_station_by_name(self, name: str) -> WeatherStation:
        for station in self._features:
            if name == station.formatted_name:
                return station
        return WeatherStation()

    def get_station_name_list(self):
        list = []
        for station in self._features:
            if WeatherUtils.ok_to_add_station(station.name):
                list.append(station.formatted_name)
        return list
