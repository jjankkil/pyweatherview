from . import station_info, weather_station


class DataModel:
    VERSION = "0.1.0"

    def __init__(self):
        self._station_list = station_info.WeatherStationList()  # all stations
        self._current_station = weather_station.WeatherStation()  # selected station

    def __repr__(self) -> str:
        """Short representation for debugging and logging."""
        return f"DataModel(stations={len(self._station_list._stations)})"

    @property
    def stations(self):
        return self._station_list._stations

    @property
    def current_station(self):
        return self._current_station

    def parse_station_list(self, station_list_json) -> bool:
        """Parse raw station list JSON into model objects.

        Returns True when parsing succeeds, False otherwise.
        """
        return self._station_list.parse(station_list_json)

    def parse_station_data(self, station_data_json) -> bool:
        """Parse detailed station observation JSON into the current station."""
        return self._current_station.parse(station_data_json)

    def set_currect_station(self, station_id):
        self._current_station._station_info = self._station_list.find_station_by_id(
            station_id
        )
