from datetime import datetime
from enum import Enum

from utils import Utils
from weatherutils import ConversionType, WeatherUtils

from . import station_info


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
            self._measured_time = WeatherUtils.timestamp_to_datetime(
                sensor_json["measuredTime"]
            )
            self._value = sensor_json["value"]
            if not sensor_json["unit"] in WeatherUtils.MISSING_UNIT:
                self._unit = sensor_json["unit"]
            if "sensorValueDescriptionFi" in sensor_json:
                self._sensor_value_description = sensor_json["sensorValueDescriptionFI"]
            return True

        except:
            pass  # todo: add error handling

        return False

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
        observation_time = WeatherUtils.timestamp_to_datetime(
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

    def find_sensor(self, sensor_name: str):
        for sensor in self.sensor_values:
            if sensor.name == sensor_name:
                return sensor
        return None

    def get_formatted_value(self, sensor_name):
        sensor = self.find_sensor(sensor_name)
        if sensor != None:
            return f"{sensor.value} {sensor.unit}"
        return ""

    def get_value(self, sensor_name, conversion_type=ConversionType.TO_INT):
        sensor = self.find_sensor(sensor_name)
        if sensor == None:
            return WeatherUtils.INVALID_VALUE
        if conversion_type == ConversionType.TO_FLOAT:
            return float(str(sensor.value))
        if conversion_type == ConversionType.TO_INT:
            return int(str(sensor.value).split(".")[0])

    def get_present_weather(self):
        pw_label = "Säätila:"
        pw_text = ""

        sensor = self.find_sensor("SADE")
        if sensor == None:
            return pw_label, pw_text

        if sensor.value >= 1.0:
            pw_label = "Sade:"
        pw_text = sensor.sensor_value_description

        return pw_label, pw_text
