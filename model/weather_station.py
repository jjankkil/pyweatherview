from datetime import datetime
from enum import Enum


class DataModel:
    VERSION_STR = "0.1.0"


class Sensor:
    INVALID_VALUE = -999

    def __init__(self):
        self.type = "r"
        self.unit = ""
        self.update_interval_s = 300
        self.data_updated = datetime(1970, 1, 1, 0, 0, 0)


class AirTemperatureSensor(Sensor):
    def __init__(self):
        super().__init__()
        self.type = "AirTemperatureSensor"
        self.unit = "°C"
        self.temperature = float(Sensor.INVALID_VALUE)
        self._temperature_change = float(Sensor.INVALID_VALUE)
        self._temperature_feels_like = float(Sensor.INVALID_VALUE)

    @property
    def Temperature(self):
        return self._temperature

    @property
    def TemperatureChange(self):
        return self._temperature_change

    @property
    def TemperatureFeelsLike(self):
        return self._temperature_feels_like


class WindSensor(Sensor):
    def __init__(self):
        super().__init__()
        self.type = "WindSensor"
        self.unit = "m/s"
        self._wind_speed = float(Sensor.INVALID_VALUE)
        self._wind_direction = float(Sensor.INVALID_VALUE)
        self._wind_direction_text = ""


class WeatherStation:
    class ObservationTimeIdx(Enum):
        LATEST = 0
        PREVIOUS = 1

    def __init__(self):
        self._station_id = 0
        self._station_name = ""
        self._observation_time = [datetime(1970, 1, 1, 0, 0, 0)] * 2

        self.sensors = []
        self.sensors.append(AirTemperatureSensor())
        self.sensors.append(WindSensor())

    @property
    def ObservationTime(self, idx: ObservationTimeIdx = ObservationTimeIdx.LATEST):
        if id > WeatherStation.ObservationTimeIdx.LATEST:
            return {}
        else:
            return self._observation_time[idx]
