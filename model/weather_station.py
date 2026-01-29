import math
from datetime import datetime
from enum import Enum

from definitions import Constants, ConversionType

from utils.utils import Utils

from . import station_info
from .helpers import ok_to_add_station


class Sensor:
    INVALID_VALUE = -999

    class SensorType(Enum):
        NOT_DEFINED = 0
        TEMPERATURE = 1
        WIND = 2

    class SensorStatus(Enum):
        MISSING = -1
        OK = 0
        NOT_OK = 1

    def __init__(self):
        # properties copied from WeatherView application:
        self._id = 0
        self._station_id = 0
        self._name = ""
        self._short_name = ""
        self._measured_time = datetime(1970, 1, 1, 0, 0, 0)
        self._value = 0.0
        self._unit = ""
        self._sensor_value_description = ""  # used for present weather
        self._sensor_status = Sensor.SensorStatus.OK

        # new properties, may be dropped:
        self._sensor_type = Sensor.SensorType.NOT_DEFINED

    def parse(self, sensor_json) -> bool:
        try:
            self._id = sensor_json["id"]
            self._station_id = sensor_json["stationId"]
            self._name = sensor_json["name"]
            self._short_name = sensor_json["shortName"]
            self._measured_time = Utils.timestamp_to_datetime(
                sensor_json["measuredTime"]
            )
            self._value = sensor_json["value"]
            if not sensor_json["unit"] in Constants.MISSING_UNIT:
                self._unit = sensor_json["unit"]
            if "sensorValueDescriptionFi" in sensor_json:
                self._sensor_value_description = sensor_json["sensorValueDescriptionFi"]
            return True

        except:
            pass  # todo: add error handling

        return False

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit

    @property
    def sensor_value_description(self) -> str:
        return self._sensor_value_description


class WeatherStation:
    class ObservationTimeIdx(Enum):
        LATEST = 0
        PREVIOUS = 1

    def __init__(self):
        self._station_info = station_info.WeatherStationInfo()
        time_now = datetime.now()
        self._data_updated_time = [time_now] * 2
        self.sensor_values = [Sensor()]

    def parse(self, weather_data) -> bool:
        # update 'data updated' times
        observation_time = Utils.timestamp_to_datetime(
            weather_data["dataUpdatedTime"]
        )
        if (
            observation_time
            != self._data_updated_time[WeatherStation.ObservationTimeIdx.PREVIOUS.value]
        ):
            self._data_updated_time[
                WeatherStation.ObservationTimeIdx.PREVIOUS.value
            ] = self._data_updated_time[WeatherStation.ObservationTimeIdx.LATEST.value]
            self._data_updated_time[WeatherStation.ObservationTimeIdx.LATEST.value] = (
                observation_time
            )

        # get sensor values
        self.sensor_values.clear()
        for sensor_json in weather_data["sensorValues"]:
            sensor_value = Sensor()
            if sensor_value.parse(sensor_json):
                self.sensor_values.append(sensor_value)

        return True

    @property
    def id(self):
        return self._station_info.id

    @property
    def formatted_name(self) -> str:
        return self._station_info.formatted_name

    @property
    def coordinates(self):
        return self._station_info.coordinates

    @property
    def data_updated_time(
        self, idx: ObservationTimeIdx = ObservationTimeIdx.LATEST
    ) -> datetime:
        if idx.value > WeatherStation.ObservationTimeIdx.LATEST.value:
            return datetime(1970, 1, 1, 0, 0, 0)
        else:
            return self._data_updated_time[idx.value]

    @property
    def seconds_until_next_update(self):
        return Utils.calculate_seconds_until_next_update(
            self._data_updated_time[
                WeatherStation.ObservationTimeIdx.LATEST.value
            ].timestamp(),
            self._data_updated_time[
                WeatherStation.ObservationTimeIdx.PREVIOUS.value
            ].timestamp(),
        )

    @property
    def air_temperature(self):
        return self.get_value("ILMA", ConversionType.TO_FLOAT)

    @property
    def air_temperature_str(self) -> str:
        return self.get_formatted_value("ILMA")

    @property
    def air_humidity(self):
        return self.get_value("ILMAN_KOSTEUS", ConversionType.TO_FLOAT)

    @property
    def temperature_change_str(self) -> str:
        return self.get_formatted_value("ILMA_DERIVAATTA")

    @property
    def wind_speed(self):
        return self.get_value("KESKITUULI", ConversionType.TO_FLOAT)

    @property
    def wind_direction(self):
        return self.get_value("TUULENSUUNTA")

    @property
    def wind_speed_str(self) -> str:
        return self.get_formatted_value("KESKITUULI")

    @property
    def wind_speed_max_str(self):
        return self.get_formatted_value("MAKSIMITUULI")

    @property
    def present_weather_code(self):
        # find "VALLITSEVA_SÄÄ" by sensor id:
        return self.get_value("100")

    @property
    def visibility(self):
        # find "NÄKYVYYS_M" by sensor id:
        return self.get_value("58")

    @property
    def visibility_str(self):
        value = self.visibility
        if value == None or value < 0:
            return ""
        elif value >= 1000:
            return f"{math.floor(value/1000)} km"
        elif value >= 100:
            return f"{math.floor(value-value%100)} m"
        else:
            return f"{math.floor(value-value%10)} m"

    def get_formatted_value(self, sensor_name):
        sensor = self._find_sensor(sensor_name)
        if sensor != None:
            return f"{sensor.value} {sensor.unit}"
        return ""

    def get_value(self, sensor_identifier: str, conversion_type=ConversionType.TO_INT):
        if sensor_identifier.isnumeric():
            sensor = self._find_sensor_by_id(int(sensor_identifier))
        else:
            sensor = self._find_sensor(sensor_identifier)

        if sensor == None:
            return Constants.INVALID_VALUE
        if conversion_type == ConversionType.TO_FLOAT:
            return float(str(sensor.value))
        if conversion_type == ConversionType.TO_INT:
            return int(str(sensor.value).split(".")[0])

    def get_present_weather(self):
        pw_label = "Säätila:"
        pw_text = ""

        sensor = self._find_sensor("SADE")
        if sensor == None:
            return pw_label, pw_text

        if sensor.value >= 1.0:
            pw_label = "Sade:"
        pw_text = sensor.sensor_value_description

        return pw_label, pw_text

    def _find_sensor(self, sensor_name: str):
        for sensor in self.sensor_values:
            if sensor.name == sensor_name:
                return sensor
        return None

    def _find_sensor_by_id(self, sensor_id: int):
        for sensor in self.sensor_values:
            if sensor.id == sensor_id:
                return sensor
        return None
