from datetime import datetime
from enum import Enum

from utils import Utils
from weatherutils import WeatherUtils

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
    def sensor_type(self) -> SensorType:
        return self._sensor_type

    @property
    def unit(self) -> str:
        return self._unit


class AirTemperature(Sensor):
    def __init__(self):
        super().__init__()
        self._sensor_type = Sensor.SensorType.TEMPERATURE
        self._unit = "°C"
        self._temperature = float(Sensor.INVALID_VALUE)
        self._temperature_change = float(Sensor.INVALID_VALUE)
        self._temperature_feels_like = float(Sensor.INVALID_VALUE)
        self._temperature_change_unit = "°C/h"

    @property
    def temperature(self) -> float:
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self.temperature = value
        self.text = f"{str(self.temperature)} {self.unit}"

    @property
    def temperature_change(self) -> float:
        return self._temperature_change

    @property
    def temperature_change_unit(self) -> str:
        return self._temperature_change_unit

    @property
    def temperature_feels_like(self) -> float:
        return self._temperature_feels_like


class Wind(Sensor):
    def __init__(self):
        super().__init__()
        self._sensor_type = Sensor.SensorType.WIND
        self._unit = "m/s"
        self._wind_speed = float(Sensor.INVALID_VALUE)
        self._wind_direction = int(Sensor.INVALID_VALUE)
        self._wind_direction_text = ""

    @property
    def speed(self) -> float:
        return self._wind_speed

    @property
    def direction(self) -> int:
        return self._wind_direction

    @property
    def direction_text(self) -> str:
        return self._wind_direction_text


class WeatherStation:
    class ObservationTimeIdx(Enum):
        LATEST = 0
        PREVIOUS = 1

    def __init__(self):
        self._station_info = station_info.WeatherStationInfo()
        self._data_updated_time = [datetime(1970, 1, 1, 0, 0, 0)] * 2
        self.sensor_values = []

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
