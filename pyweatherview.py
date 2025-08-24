import json
import math
import sys
from datetime import datetime
from enum import Enum

import requests
from dateutil import tz
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# local modules:
from definitions import Constants
from utils import Utils
from weatherutils import WeatherUtils

LAYOUT_STYLES = """
    QLabel, QPushButton{
        font-family: calibri;
    }
    QLabel#station_list_label{
        font-size: 20px;
    }
    QComboBox#station_list{
        font-size: 17px;
    }
    QLabel#observation_time_label{
        font-size: 20px;
    }
    QLabel#observation_time_value{
        font-size: 20px;
    }
    QLabel#temperature_label{
        font-size: 20px;
    }
    QLabel#temperature_value{
        font-size: 20px;
    }
    QLabel#avg_wind_label{
        font-size: 20px;
    }
    QLabel#avg_wind_value{
        font-size: 20px;
    }
    QLabel#max_wind_label{
        font-size: 20px;
    }
    QLabel#max_wind_value{
        font-size: 20px;
    }
    QLabel#visibility_label{
        font-size: 20px;
    }
    QLabel#visibility_value{
        font-size: 20px;
    }
    QLabel#present_weather_label{
        font-size: 20px;
    }
    QLabel#present_weather_value{
        font-size: 20px;
    }
    QLabel#forecast_label{
        font-size: 20px;
    }
    QLabel#error_message{
        font-size: 20px;
        font-style: italic;
    }
    QPushButton#update_button{
        font-size: 20px;
        font-weight: bold;
    }
    QLabel#update_time_value{
        font-size: 15px;
    }
"""


class WeatherApp(QWidget):
    SETTINGS_FILE_NAME = "settings.json"
    SHORT_TIME_FORMAT = "%H:%M"
    TIME_FORMAT = "%H:%M:%S"
    DATE_TIME_FORMAT = "%d.%m.%Y %H:%M"
    FORECAST_CNT = 3
    SYMBOL_CNT = FORECAST_CNT + 1
    STATION_UPDATE_DELAY = 60

    class ConversionType(Enum):
        TO_INT = 1
        TO_FLOAT = 2

    def __init__(self):
        super().__init__()
        QApplication.instance().aboutToQuit.connect(self._cleanup)
        Utils.set_taskbar_icon()

        self.station_list_label = QLabel("Havaintoasema:", self)
        self.station_list = QComboBox(self)
        self.observation_time_label = QLabel("Havantoaika:", self)
        self.observation_time_value = QLabel(self)
        self.temperature_label = QLabel("Lämpötila:", self)
        self.temperature_value = QLabel(self)
        self.avg_wind_label = QLabel("Keskituuli:", self)
        self.avg_wind_value = QLabel(self)
        self.max_wind_label = QLabel("Max. tuuli:", self)
        self.max_wind_value = QLabel(self)
        self.visibility_label = QLabel("Näkyvyys:", self)
        self.visibility_value = QLabel(self)
        self.present_weather_label = QLabel("Säätila:", self)
        self.present_weather_value = QLabel(self)
        self.forecast_label = QLabel("Ennuste paikkakunnalle", self)
        self.weather_symbols = [
            {"label": QLabel(f" \n ", self), "symbol": QLabel(self)}
            for i in range(WeatherApp.SYMBOL_CNT)
        ]
        self.error_message = QLabel(self)
        self.update_button = QPushButton("Päivitä", self)
        self.update_time_value = QLabel(self)
        self.settings = Utils.load_settings(WeatherApp.SETTINGS_FILE_NAME)

        self.init_ui()
        self.init_data()
        self.station_list.currentIndexChanged.connect(self.update_weather)
        self.update_button.clicked.connect(self.update_weather)
        self.apply_settings()

        self.timer = QTimer()
        self.update_interval_s = 60  # initially 1 minute update interval
        self.timer.timeout.connect(self.timer_func)
        self.timer.start(self.update_interval_s * 1000)

    def timer_func(self):
        self.update_button.click()

    def _cleanup(self):
        self.settings["current_station"] = self.station_list.currentText()
        data = self.settings
        Utils.save_settings(WeatherApp.SETTINGS_FILE_NAME, data)

    def apply_settings(self):
        if len(self.settings.items()) == 0:
            return

        station_name = self.settings["current_station"]
        self.station_list.setCurrentText(station_name)

    def init_ui(self):
        self.setWindowTitle("Tiesää")
        self.setWindowIcon(QtGui.QIcon("pyweatherview.ico"))
        self.setStyleSheet(LAYOUT_STYLES)

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.station_list_label, 0, 0)
        grid_layout.addWidget(self.station_list, 0, 1)
        grid_layout.addWidget(self.observation_time_label, 1, 0)
        grid_layout.addWidget(self.observation_time_value, 1, 1)
        grid_layout.addWidget(self.temperature_label, 2, 0)
        grid_layout.addWidget(self.temperature_value, 2, 1)
        grid_layout.addWidget(self.avg_wind_label, 3, 0)
        grid_layout.addWidget(self.avg_wind_value, 3, 1)
        grid_layout.addWidget(self.max_wind_label, 4, 0)
        grid_layout.addWidget(self.max_wind_value, 4, 1)
        grid_layout.addWidget(self.visibility_label, 5, 0)
        grid_layout.addWidget(self.visibility_value, 5, 1)
        grid_layout.addWidget(self.present_weather_label, 6, 0)
        grid_layout.addWidget(self.present_weather_value, 6, 1)

        weather_symbol_layout = QHBoxLayout()
        for i in range(WeatherApp.SYMBOL_CNT):
            weather_symbol_layout.addWidget(self.weather_symbols[i]["symbol"])

        weather_label_layout = QHBoxLayout()
        for i in range(WeatherApp.SYMBOL_CNT):
            weather_label_layout.addWidget(self.weather_symbols[i]["label"])

        main_layout = QVBoxLayout()
        main_layout.addLayout(grid_layout)
        grid_layout.addWidget(self.forecast_label)
        main_layout.addLayout(weather_symbol_layout)
        main_layout.addLayout(weather_label_layout)
        main_layout.addWidget(self.error_message)
        main_layout.addWidget(self.update_button)
        main_layout.addWidget(self.update_time_value)
        self.setLayout(main_layout)

        self.station_list_label.setAlignment(Qt.AlignLeft)
        self.observation_time_label.setAlignment(Qt.AlignLeft)
        self.observation_time_value.setAlignment(Qt.AlignLeft)
        self.temperature_label.setAlignment(Qt.AlignLeft)
        self.temperature_value.setAlignment(Qt.AlignLeft)
        self.temperature_value.setWordWrap(True)
        self.avg_wind_label.setAlignment(Qt.AlignLeft)
        self.avg_wind_value.setAlignment(Qt.AlignLeft)
        self.max_wind_label.setAlignment(Qt.AlignLeft)
        self.max_wind_value.setAlignment(Qt.AlignLeft)
        self.visibility_label.setAlignment(Qt.AlignLeft)
        self.visibility_value.setAlignment(Qt.AlignLeft)
        self.present_weather_label.setAlignment(Qt.AlignLeft)
        self.present_weather_value.setAlignment(Qt.AlignLeft)
        self.forecast_label.setAlignment(Qt.AlignCenter)

        for i in range(WeatherApp.SYMBOL_CNT):
            self.weather_symbols[i]["label"].setFont(QtGui.QFont("", 15))
            self.weather_symbols[i]["label"].setAlignment(Qt.AlignCenter)
            self.weather_symbols[i]["symbol"].setFont(QtGui.QFont("Segoe UI emoji", 60))
            self.weather_symbols[i]["symbol"].setAlignment(Qt.AlignCenter)

        self.error_message.setAlignment(Qt.AlignCenter)
        self.update_time_value.setAlignment(Qt.AlignCenter)

        self.station_list_label.setObjectName("station_list_label")
        self.station_list.setObjectName("station_list")
        self.observation_time_label.setObjectName("observation_time_label")
        self.observation_time_value.setObjectName("observation_time_value")
        self.temperature_label.setObjectName("temperature_label")
        self.temperature_value.setObjectName("temperature_value")
        self.avg_wind_label.setObjectName("avg_wind_label")
        self.avg_wind_value.setObjectName("avg_wind_value")
        self.max_wind_label.setObjectName("max_wind_label")
        self.max_wind_value.setObjectName("max_wind_value")
        self.visibility_label.setObjectName("visibility_label")
        self.visibility_value.setObjectName("visibility_value")
        self.present_weather_label.setObjectName("present_weather_label")
        self.present_weather_value.setObjectName("present_weather_value")
        self.forecast_label.setObjectName("forecast_label")
        for i in range(WeatherApp.SYMBOL_CNT):
            self.weather_symbols[i]["symbol"].setObjectName(f"forecast_symbol_{i}")
        self.error_message.setObjectName("error_message")
        self.update_button.setObjectName("update_button")
        self.update_time_value.setObjectName("update_time_value")

        # self.station_list.setEditable(True)
        # self.station_list.setInsertPolicy(QComboBox.InsertAlphabetically)

    def init_data(self):
        station_data = self.get_weather_stations()
        self.display_weather_stations(station_data)

    def update_weather(self):
        self.error_message.clear()
        self.display_road_weather(self.get_data())

    def get_weather_stations(self):
        """Get a list containing all weather stations from from Liikennevirasto Open Data API.
        Returns a JSON array of stations, or None on error."""
        try:
            response = requests.get(Constants.STATION_LIST_URL)
            response.raise_for_status()
            json_data = response.json()
            return json_data["features"]

        except:
            error_json = json.loads(response.text)
            self.display_error(f"Failed to get station list: {error_json["message"]}")
            return None

    def get_data(self):
        station_data = self.get_road_weather().json()
        city_data = self.get_city_weather().json()
        forecast = self.get_forecast().json()
        return station_data, city_data, forecast

    def get_road_weather(self):
        """Get weather data from Liikennevirasto Open Data API"""
        station_id = self.station_list.currentData()["station_id"]
        url = Constants.WEATHER_STATION_URL.format(station_id)
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except:
            error_json = json.loads(response.text)
            self.display_error(f"Road weather request failed: {error_json["message"]}")
            return json.loads("{}")

    def get_city_weather(self):
        """Get weather data from Open Weathermap API.
        This is needed for the present weather symbol."""
        city = WeatherUtils.get_station_city(self.station_list.currentText())
        url = Constants.OPENWEATHERMAP_URL.format(
            city, self.settings["openweathermap_api_key"]
        )
        try:
            response = requests.get(url)
            response.raise_for_status()
        except:
            error_json = json.loads(response.text)
            self.display_error(f"City weather request failed: {error_json["message"]}")
        return response

    def get_forecast(self):
        """Get weather forecast from Open Weathermap API"""
        location = self.station_list.currentData()["location"]
        url = Constants.FORERCAST_URL.format(
            location["lat"],
            location["lon"],
            self.settings["openweathermap_api_key"],
        )
        response = requests.get(url)
        if response.status_code != 200:
            error_json = json.loads(response.text)
            self.display_error(f"Forecast request failed: {error_json["message"]}")
            return json.loads("{}")
        return response

    def _clear_ui_components(self):
        self.observation_time_value.clear()
        self.temperature_value.clear()
        self.avg_wind_value.clear()
        self.max_wind_value.clear()
        self.visibility_value.clear()
        self.present_weather_value.clear()
        for i in range(WeatherApp.SYMBOL_CNT):
            self.weather_symbols[i]["label"].clear()
            self.weather_symbols[i]["symbol"].clear()

    def display_error(self, message):
        self._clear_ui_components()
        self.error_message.setText(message)

    def display_weather_stations(self, json_data):
        """Populate the station list UI component from the given JSON array"""
        self.station_list.clear()
        for station in json_data:
            station_name = station["properties"]["name"]
            if WeatherUtils.ok_to_add_station(station_name):
                formatted_name = WeatherUtils.format_station_name(station_name)
                self.station_list.addItem(
                    formatted_name,
                    {
                        "station_id": station["id"],
                        "station_data_update_time": datetime.now(
                            tz.tzutc()
                        ).timestamp(),
                        "city": WeatherUtils.get_station_city(formatted_name),
                        "location": {
                            "lon": round(station["geometry"]["coordinates"][0], 2),
                            "lat": round(station["geometry"]["coordinates"][1], 2),
                        },
                    },
                )
        self.station_list.model().sort(0, Qt.SortOrder.AscendingOrder)

    def get_formatted_sensor_value(self, sensor_values_json, sensor_name):
        sensor = self.find_sensor(sensor_values_json, sensor_name)
        if sensor != None:
            return f"{sensor["value"]} {sensor["unit"]}"
        return ""

    def get_raw_sensor_value(
        self,
        sensor_values_json,
        sensor_name,
        conversion_type=ConversionType.TO_INT,
    ):
        sensor = self.find_sensor(sensor_values_json, sensor_name)
        if sensor == None:
            return None
        if conversion_type == WeatherApp.ConversionType.TO_FLOAT:
            return float(str(sensor["value"]))
        if conversion_type == WeatherApp.ConversionType.TO_INT:
            return int(str(sensor["value"]).split(".")[0])

    def _calculate_feels_like_temperature(self, json_data) -> float:
        wind_speed = self.get_raw_sensor_value(
            json_data["sensorValues"], "KESKITUULI", WeatherApp.ConversionType.TO_FLOAT
        )
        relative_humidity = self.get_raw_sensor_value(
            json_data["sensorValues"],
            "ILMAN_KOSTEUS",
            WeatherApp.ConversionType.TO_FLOAT,
        )
        air_temperature = self.get_raw_sensor_value(
            json_data["sensorValues"], "ILMA", WeatherApp.ConversionType.TO_FLOAT
        )
        feels_like = WeatherUtils.fmi_feels_like_temperature(
            wind_speed, relative_humidity, air_temperature
        )
        return feels_like

    def display_road_weather(self, data: tuple[any, any, any]):
        weather_data = data[0]
        city_data = data[1]
        forecast = data[2]

        # -------------------------------------------------------------------
        # get data from json
        #
        observation_time_utc = datetime.strptime(
            weather_data["dataUpdatedTime"], "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=tz.tzutc())

        # calculate how long we need to wait until the next update and add some slack
        previous_observation_time_ts = self.station_list.currentData()[
            "station_data_update_time"
        ]
        waiting_time_s = Utils.calculate_seconds_until_next_update(
            observation_time_utc.timestamp(), previous_observation_time_ts
        )
        if waiting_time_s > 0:
            self.update_interval_s = int(str(f"{waiting_time_s:.0f}"))
            self.timer.start(
                (self.update_interval_s + WeatherApp.STATION_UPDATE_DELAY) * 1000
            )
        item_data = self.station_list.currentData()
        item_data["station_data_update_time"] = observation_time_utc.timestamp()
        self.station_list.setItemData(self.station_list.currentIndex(), item_data)

        air_temperature = self.get_formatted_sensor_value(
            weather_data["sensorValues"], "ILMA"
        )
        air_temperature_change = self.get_formatted_sensor_value(
            weather_data["sensorValues"], "ILMA_DERIVAATTA"
        )
        feels_like_temperature = self._calculate_feels_like_temperature(weather_data)

        wind_avg = self.get_formatted_sensor_value(
            weather_data["sensorValues"], "KESKITUULI"
        )
        wind_deg = self.get_raw_sensor_value(
            weather_data["sensorValues"], "TUULENSUUNTA"
        )
        wind_max = self.get_formatted_sensor_value(
            weather_data["sensorValues"], "MAKSIMITUULI"
        )

        weather_id = 0
        if "weather" in city_data:
            weather_id = city_data["weather"][0]["id"]

        present_weather = self.get_present_weather(weather_data["sensorValues"])
        humidity = self.get_raw_sensor_value(
            weather_data["sensorValues"], "ILMAN_KOSTEUS"
        )
        visibility = self.get_raw_sensor_value(
            weather_data["sensorValues"], "NÄKYVYYS_M"
        )

        # get forecast time, temperature and weather_id
        forecasts = [
            [
                datetime.fromtimestamp(forecast["list"][i]["dt"]).strftime(
                    WeatherApp.SHORT_TIME_FORMAT
                ),
                f"{forecast["list"][i]["main"]["temp"] - 273.15:.0f}",
                forecast["list"][i]["weather"][0]["id"],
            ]
            for i in range(WeatherApp.FORECAST_CNT)
        ]

        # -------------------------------------------------------------------
        # update ui components
        #
        self.observation_time_value.setText(
            observation_time_utc.astimezone(tz.tzlocal()).strftime(
                WeatherApp.DATE_TIME_FORMAT
            )
        )

        temperature_str = ""
        if feels_like_temperature == WeatherUtils.INVALID_VALUE:
            temperature_str = f"{air_temperature}"
        else:
            temperature_str = (
                f"{air_temperature}, tuntuu kuin {feels_like_temperature:.1f} °C"
            )
        if air_temperature_change != "":
            temperature_str += f",\nmuutos {air_temperature_change}"
        self.temperature_value.setText(temperature_str)

        if wind_avg == "":
            self.avg_wind_value.setText("")
        else:
            self.avg_wind_value.setText(
                f"{wind_avg}, suunta {wind_deg}° {WeatherUtils.wind_direction_as_text(wind_deg)}"
            )
        self.max_wind_value.setText(wind_max)

        if weather_id > 0:
            ts = observation_time_utc.astimezone(tz.tzlocal()).strftime(
                WeatherApp.SHORT_TIME_FORMAT
            )
            temp = self.get_raw_sensor_value(
                weather_data["sensorValues"], "ILMA", WeatherApp.ConversionType.TO_INT
            )
            self.weather_symbols[0]["label"].setText(f"{ts}\n{temp:.0f} °C")
            self.weather_symbols[0]["symbol"].setText(
                WeatherUtils.get_weather_symbol(weather_id)
            )
        else:
            self.weather_symbols[0]["label"].setText("")
            self.weather_symbols[0]["symbol"].setText("")

        if present_weather[1] != "":
            self.present_weather_label.setText(present_weather[0])
            self.present_weather_value.setText(
                f"{present_weather[1]}, suht. kosteus {humidity}%"
            )

        if visibility == None:
            self.visibility_value.setText("")
        elif visibility >= 1000:
            self.visibility_value.setText(f"{math.floor(visibility/1000)} km")
        elif visibility >= 100:
            self.visibility_value.setText(f"{math.floor(visibility-visibility%100)} m")
        else:
            self.visibility_value.setText(f"{math.floor(visibility-visibility%10)} m")

        if "name" in city_data:
            self.forecast_label.setText(
                f"\nEnnuste paikkakunnalle {city_data["name"]}:"
            )
        else:
            self.forecast_label.setText("")
        for i in range(WeatherApp.FORECAST_CNT):
            self.weather_symbols[i + 1]["label"].setText(
                f"{forecasts[i][0]}\n{forecasts[i][1]} °C"
            )
            self.weather_symbols[i + 1]["symbol"].setText(
                f"{WeatherUtils.get_weather_symbol(forecasts[i][2])}"
            )

        self.update_time_value.setText(datetime.now().strftime(WeatherApp.TIME_FORMAT))

    def get_present_weather(self, sensor_values_json):
        pw_label = "Säätila:"
        pw_text = ""

        sensor = self.find_sensor(sensor_values_json, "SADE")
        if sensor == None:
            return pw_label, pw_text

        if sensor["value"] >= 1.0:
            pw_label = "Sade:"
        pw_text = sensor["sensorValueDescriptionFi"]

        return pw_label, pw_text

    def find_sensor(self, sensor_values_json, sensor_name):
        for sensor in sensor_values_json:
            if sensor["name"] == sensor_name:
                return sensor
        return None


if __name__ == "__main__":
    if not Utils.CheckPythonVersion():
        sys.exit()

    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
