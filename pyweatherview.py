import json
import math
import sys
from datetime import datetime

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
from definitions import Constants, Formats, Urls
from model import data_model
from utils import Utils
from weatherutils import ConversionType, WeatherUtils

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
    def __init__(self):
        super().__init__()
        instance = QApplication.instance()
        if instance != None:  # 'None check' keeps Pylance happy
            instance.aboutToQuit.connect(self._cleanup)
        Utils.set_taskbar_icon()

        self._data_model = data_model.DataModel()

        self.current_station_id = 0
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
            for i in range(Constants.SYMBOL_CNT)
        ]
        self.error_message = QLabel(self)
        self.update_button = QPushButton("Päivitä", self)
        self.update_time_value = QLabel(self)
        self.settings = Utils.load_settings(Constants.SETTINGS_FILE_NAME)

        self._init_ui()
        self._init_station_list()
        self.station_list.currentIndexChanged.connect(self._on_station_selected)
        self.update_button.clicked.connect(self._on_station_selected)
        self._apply_settings()

        self.timer = QTimer()
        self.update_interval_s = 60  # initially 1 minute update interval
        self.timer.timeout.connect(self.timer_func)
        self.timer.start(self.update_interval_s * 1000)

    def timer_func(self):
        self.update_button.click()

    def _cleanup(self):
        self.settings["current_station"] = self.station_list.currentText()
        data = self.settings
        Utils.save_settings(Constants.SETTINGS_FILE_NAME, data)

    def _apply_settings(self):
        if len(self.settings.items()) == 0:
            return
        station_name = self.settings["current_station"]
        self.station_list.setCurrentText(station_name)

    def _init_ui(self):
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
        for i in range(Constants.SYMBOL_CNT):
            weather_symbol_layout.addWidget(self.weather_symbols[i]["symbol"])

        weather_label_layout = QHBoxLayout()
        for i in range(Constants.SYMBOL_CNT):
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

        AlignLeft = Qt.AlignmentFlag.AlignLeft
        AlignCenter = Qt.AlignmentFlag.AlignCenter
        self.station_list_label.setAlignment(AlignLeft)
        self.observation_time_label.setAlignment(AlignLeft)
        self.observation_time_value.setAlignment(AlignLeft)
        self.temperature_label.setAlignment(AlignLeft)
        self.temperature_value.setAlignment(AlignLeft)
        self.temperature_value.setWordWrap(True)
        self.avg_wind_label.setAlignment(AlignLeft)
        self.avg_wind_value.setAlignment(AlignLeft)
        self.max_wind_label.setAlignment(AlignLeft)
        self.max_wind_value.setAlignment(AlignLeft)
        self.visibility_label.setAlignment(AlignLeft)
        self.visibility_value.setAlignment(AlignLeft)
        self.present_weather_label.setAlignment(AlignLeft)
        self.present_weather_value.setAlignment(AlignLeft)
        self.forecast_label.setAlignment(AlignCenter)

        for i in range(Constants.SYMBOL_CNT):
            self.weather_symbols[i]["label"].setFont(QtGui.QFont("", 15))
            self.weather_symbols[i]["label"].setAlignment(AlignCenter)
            self.weather_symbols[i]["symbol"].setFont(QtGui.QFont("Segoe UI emoji", 60))
            self.weather_symbols[i]["symbol"].setAlignment(AlignCenter)

        self.error_message.setAlignment(AlignCenter)
        self.update_time_value.setAlignment(AlignCenter)

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
        for i in range(Constants.SYMBOL_CNT):
            self.weather_symbols[i]["symbol"].setObjectName(f"forecast_symbol_{i}")
        self.error_message.setObjectName("error_message")
        self.update_button.setObjectName("update_button")
        self.update_time_value.setObjectName("update_time_value")

        # self.station_list.setEditable(True)
        # self.station_list.setInsertPolicy(QComboBox.InsertAlphabetically)

    def _init_station_list(self):
        stations_json = self._get_weather_stations()
        self._data_model.parse_station_list(stations_json)
        self._display_weather_stations(self._data_model)

    def _on_station_selected(self):
        self.error_message.clear()

        # If the user has changed the station, clear all UI components
        station_id = self.station_list.currentData()["station_id"]
        if station_id != self._data_model.current_station.id:
            self._data_model.set_currect_station(station_id)
            self._clear_ui_components()
            QApplication.processEvents()

        # get the data from the APIs
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            data = self._get_weather_data()
            self._display_weather_data(data[0], data[1])
        except Exception as e:
            self._display_error(f"Error updating weather: {e}")
        finally:
            QApplication.restoreOverrideCursor()

    def _get_weather_stations(self):
        """Get a list containing all weather stations from from Liikennevirasto Open Data API.
        Returns a JSON array of stations, or None on error."""

        response = requests.Response()  # get rid of pylint warning
        try:
            response = requests.get(Urls.STATION_LIST_URL)
            response.raise_for_status()
            json_data = response.json()
            return json_data["features"]

        except:
            error_json = json.loads(response.text)
            self._display_error(f"Failed to get station list: {error_json["message"]}")
            return None

    def _get_weather_data(self):
        station_data = self._get_road_weather().json()
        self._data_model.parse_station_data(station_data)

        city_data = self._get_city_weather().json()
        forecast = self._get_forecast().json()
        return city_data, forecast

    def _get_road_weather(self):
        """Get weather data from Liikennevirasto Open Data API"""

        station_id = self.station_list.currentData()["station_id"]
        url = Urls.WEATHER_STATION_URL.format(station_id)
        response = requests.Response()
        try:
            response = requests.get(url)
            response.raise_for_status()
            # self._data_model.parse_station_data(response.json())
            return response
        except:
            error_json = json.loads(response.text)
            self._display_error(f"Road weather request failed: {error_json["message"]}")
            return json.loads("{}")

    def _get_city_weather(self):
        """Get weather data from Open Weathermap API.
        This is needed for the present weather symbol."""

        city = WeatherUtils.get_station_city(self.station_list.currentText())
        url = Urls.OPENWEATHERMAP_URL.format(
            city, self.settings["openweathermap_api_key"]
        )
        response = requests.Response()
        try:
            response = requests.get(url)
            if response.status_code == 404:
                location = self._data_model.current_station.coordinates
                url = Urls.OPENWEATHERMAP_LOCATION_URL.format(
                    location.latitude,
                    location.longitude,
                    self.settings["openweathermap_api_key"],
                )
                response = requests.get(url)
                response.raise_for_status()
        except:
            error_json = json.loads(response.text)
            self._display_error(f"City weather request failed: {error_json["message"]}")
        return response

    def _get_forecast(self):
        """Get weather forecast from Open Weathermap API"""
        location = self._data_model.current_station.coordinates
        url = Urls.FORERCAST_URL.format(
            location.latitude,
            location.longitude,
            self.settings["openweathermap_api_key"],
        )
        response = requests.get(url)
        if response.status_code != 200:
            error_json = json.loads(response.text)
            self._display_error(f"Forecast request failed: {error_json["message"]}")
            return json.loads("{}")
        return response

    def _clear_ui_components(self):
        self.observation_time_value.clear()
        self.temperature_value.clear()
        self.avg_wind_value.clear()
        self.max_wind_value.clear()
        self.visibility_value.clear()
        self.present_weather_value.clear()
        self.forecast_label.clear()
        for i in range(Constants.SYMBOL_CNT):
            self.weather_symbols[i]["label"].clear()
            self.weather_symbols[i]["symbol"].clear()

    def _display_error(self, message):
        self._clear_ui_components()
        self.error_message.setText(message)

    def _display_weather_stations(self, data_model: data_model.DataModel):
        """Populate the station list UI component from the given data model object"""
        self.station_list.clear()

        for station in data_model.stations:
            if WeatherUtils.ok_to_add_station(station.name):
                self.station_list.addItem(
                    station.formatted_name, {"station_id": station.id}
                )

        # sort the combo box:
        list_model = self.station_list.model()
        if list_model != None:  # 'None check' keeps Pylance happy
            list_model.sort(0, Qt.SortOrder.AscendingOrder)

    def _get_current_weather_id(self, city_data):
        id = 0
        if "weather" in city_data:
            id = city_data["weather"][0]["id"]
        return id

    def _get_3h_forecast(self, forecast_json):
        forecast = [
            [
                datetime.fromtimestamp(forecast_json["list"][i]["dt"]).strftime(
                    Formats.SHORT_TIME_FORMAT
                ),
                f"{forecast_json["list"][i]["main"]["temp"] - 273.15:.0f}",
                forecast_json["list"][i]["weather"][0]["id"],
            ]
            for i in range(Constants.FORECAST_CNT)
        ]
        return forecast

    def _get_forecast_label(self, city_data):
        if "name" in city_data:
            return f"\nEnnuste paikkakunnalle {city_data["name"]}:"
        return ""

    def _display_weather_data(self, city_data, forecast_data):
        station = self._data_model.current_station

        # calculate how long we need to wait until the next update and add some slack
        waiting_time_s = station.seconds_until_next_update
        if waiting_time_s > 0:
            self.update_interval_s = int(str(f"{waiting_time_s:.0f}"))
            self.timer.start(
                (self.update_interval_s + Constants.STATION_UPDATE_DELAY) * 1000
            )

        feels_like_temperature = WeatherUtils.fmi_feels_like_temperature(
            station.wind_speed, station.air_humidity, station.air_temperature
        )

        self.observation_time_value.setText(
            station.data_updated_time.astimezone(tz.tzlocal()).strftime(
                Formats.DATE_TIME_FORMAT
            )
        )

        temperature_str = ""
        if feels_like_temperature == WeatherUtils.INVALID_VALUE:
            temperature_str = station.air_temperature_str
        else:
            temperature_str = f"{station.air_temperature_str}, tuntuu kuin {feels_like_temperature:.1f} °C"
        if station.temperature_change_str != "":
            temperature_str += f",\nmuutos {station.temperature_change_str}"
        self.temperature_value.setText(temperature_str)

        if station.wind_speed_str == "":
            self.avg_wind_value.setText("")
        else:
            self.avg_wind_value.setText(
                f"{station.wind_speed_str}, suunta {station.wind_direction}° {WeatherUtils.wind_direction_as_text(station.wind_direction)}"
            )
        self.max_wind_value.setText(station.wind_speed_max_str)

        current_weather_id = self._get_current_weather_id(city_data)
        if current_weather_id > 0:
            ts = station.data_updated_time.astimezone(tz.tzlocal()).strftime(
                Formats.SHORT_TIME_FORMAT
            )
            self.weather_symbols[0]["label"].setText(
                f"{ts}\n{station.air_temperature:.0f} °C"
            )
            self.weather_symbols[0]["symbol"].setText(
                WeatherUtils.get_weather_symbol(current_weather_id)
            )
        else:
            self.weather_symbols[0]["label"].setText("")
            self.weather_symbols[0]["symbol"].setText("")

        present_weather = station.get_present_weather()
        if present_weather[1] != "":
            self.present_weather_label.setText(present_weather[0])
            self.present_weather_value.setText(
                f"{present_weather[1]}, suht. kosteus {station.air_humidity:.0f}%"
            )

        self.visibility_value.setText(station.visibility_str)

        self.forecast_label.setText(self._get_forecast_label(city_data))
        forecast = self._get_3h_forecast(forecast_data)
        for i in range(Constants.FORECAST_CNT):
            self.weather_symbols[i + 1]["label"].setText(
                f"{forecast[i][0]}\n{forecast[i][1]} °C"
            )
            self.weather_symbols[i + 1]["symbol"].setText(
                f"{WeatherUtils.get_weather_symbol(forecast[i][2])}"
            )

        self.update_time_value.setText(datetime.now().strftime(Formats.TIME_FORMAT))


if __name__ == "__main__":
    if not Utils.CheckPythonVersion():
        sys.exit()

    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
