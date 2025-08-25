from datetime import datetime
from enum import Enum


class DataModel:
    VERSION_STR = "0.1.0"


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

    __instance_counter = 0

    def __init__(self):
        Sensor.__instance_counter += 1
        self._id = Sensor.__instance_counter
        self._station_id = 0
        self._sensor_type = Sensor.SensorType.NOT_DEFINED
        self._sensor_status = Sensor.SensorStatus.OK

        self._name = ""
        self._short_name = ""
        self._value_description = "puuttuu"

        self._value = 0.0
        self._unit = ""
        self.text = ""
        self.update_interval_s = 300
        self.data_updated = datetime(1970, 1, 1, 0, 0, 0)

    @property
    def sensor_type(self) -> SensorType:
        return self._sensor_type

    @property
    def unit(self) -> str:
        return self._unit


class AirTemperatureSensor(Sensor):
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


class WindSensor(Sensor):
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
        self._station_id = 0
        self._station_name = ""
        self._data_updated_time = [datetime(1970, 1, 1, 0, 0, 0)] * 2

        self.sensors = []
        self.sensors.append(AirTemperatureSensor())
        self.sensors.append(WindSensor())

    @property
    def data_updated_time(
        self, idx: ObservationTimeIdx = ObservationTimeIdx.LATEST
    ) -> datetime:
        if idx.value > WeatherStation.ObservationTimeIdx.LATEST.value:
            return datetime(1970, 1, 1, 0, 0, 0)
        else:
            return self._data_updated_time[idx.value]

    def Parse(self, metadata_json) -> bool:
        return True
