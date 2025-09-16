import json
import sys
from datetime import datetime, timedelta

from dateutil import tz
from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QTimer, QTranslator
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# local modules:
from definitions import Constants, Formats, Styles
from model import data_model
from utils import Utils
from weatherutils import Requestor, WeatherUtils

# indices to language list:
FI = 0
EN = 1


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        instance = QApplication.instance()
        if instance != None:
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
        self.forecast_label = QLabel(self)
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
        self._apply_settings()
        self.station_list.currentIndexChanged.connect(self._on_station_selected)
        self.update_button.clicked.connect(self._on_station_selected)

        self.timer = QTimer()
        self.update_interval_s = Constants.DEFAULT_POLLING_INTERVAL_S
        self.timer.timeout.connect(self.timer_func)
        self.timer.start(self.update_interval_s * 1000)
        self._on_station_selected()

        # set up localised ui texts:
        self._ui_languages = [
            ("Suomi", ""),
            ("English", "fi-eng"),
        ]
        self._translator = QTranslator(self)

        self.context_menu = QMenu(self)
        self.ui_finnish = self.context_menu.addAction(self._ui_languages[FI][0])
        self.ui_finnish.setCheckable(True)
        self.ui_finnish.triggered.connect(self.__select_ui_finnish)

        self.ui_english = self.context_menu.addAction(self._ui_languages[EN][0])
        self.ui_english.setCheckable(True)
        self.ui_english.triggered.connect(self.__select_ui_english)

        initial_language = self.settings["ui_language"]
        if initial_language == self._ui_languages[FI][1]:
            self.__select_ui_finnish()
        else:
            self.__select_ui_english()

    def contextMenuEvent(self, event):
        # show the popup menu
        self.context_menu.exec(event.globalPos())

    def __select_language(self, language_id):
        self._set_ui_language(language_id)
        self._set_ui_labels()
        self.settings["ui_language"] = language_id

    def __select_ui_finnish(self):
        self.setWindowTitle("Tiesää")
        language_id = self._ui_languages[FI][1]
        self.__select_language(language_id)
        self.ui_finnish.setChecked(True)
        self.ui_english.setChecked(False)

    def __select_ui_english(self):
        self.setWindowTitle("Road Weather")
        language_id = self._ui_languages[EN][1]
        self.__select_language(language_id)
        self.ui_finnish.setChecked(False)
        self.ui_english.setChecked(True)

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
        self.setWindowIcon(QtGui.QIcon("pyweatherview.ico"))

        try:
            file_name = "pyweatherview.qss"
            with open(file_name, "r") as f:
                self.setStyleSheet(f.read())
        except:
            self.setStyleSheet(Styles.DEFAULT)

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

        AlignCenter = Qt.AlignmentFlag.AlignCenter
        for i in range(Constants.SYMBOL_CNT):
            self.weather_symbols[i]["label"].setFont(QtGui.QFont("", 15))
            self.weather_symbols[i]["label"].setAlignment(AlignCenter)
            self.weather_symbols[i]["symbol"].setFont(QtGui.QFont("Segoe UI emoji", 55))
            self.weather_symbols[i]["symbol"].setAlignment(AlignCenter)

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

    def _set_ui_language(self, language_id):
        instance = QApplication.instance()
        if instance != None:
            instance.removeTranslator(self._translator)
            if language_id:
                self._translator.load(language_id)
                instance.installTranslator(self._translator)

    def _set_ui_labels(self):
        self.station_list_label.setText(
            QApplication.translate("WeatherApp", "Havaintoasema:")
        )
        self.observation_time_label.setText(
            QApplication.translate("WeatherApp", "Havaintoaika:")
        )
        self.temperature_label.setText(
            QApplication.translate("WeatherApp", "Lämpötila:")
        )
        self.avg_wind_label.setText(QApplication.translate("WeatherApp", "Keskituuli:"))
        self.max_wind_label.setText(QApplication.translate("WeatherApp", "Max. tuuli:"))
        self.visibility_label.setText(QApplication.translate("WeatherApp", "Näkyvyys:"))
        self.present_weather_label.setText(
            QApplication.translate("WeatherApp", "Säätila:")
        )

        self.forecast_label.setText(
            "{0} {1}:".format(
                QApplication.translate("WeatherApp", "Ennuste paikkakunnalle"),
                WeatherUtils.get_station_city(self.station_list.currentText()),
            )
        )

        self.update_button.setText(QApplication.translate("WeatherApp", "Päivitä"))

    def _init_station_list(self):
        req = Requestor()
        stations_json = req.get_weather_stations()
        self._data_model.parse_station_list(stations_json)
        if req.has_error:
            self._display_error(f"Failed to get station list: {req.error_message}")
        else:
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

    def _get_weather_data(self):
        req = Requestor()

        station_id = self.station_list.currentData()["station_id"]
        station_data = req.get_road_weather(station_id)
        if req.has_error:
            self._display_error(f"Road weather request failed: {req.error_message}")
            return [json.loads("{}"), json.loads("{}")]
        self._data_model.parse_station_data(station_data)

        # todo: add city weather and forecast to data model
        api_key = self.settings["openweathermap_api_key"]
        if api_key == "":
            city_data = json.loads("{}")
            forecast = json.loads("{}")
        else:
            city = WeatherUtils.get_station_city(self.station_list.currentText())
            coordinates = self._data_model.current_station.coordinates

            city_data = req.get_city_weather(city, coordinates, api_key)
            if req.has_error:
                self._display_error(f"City weather request failed: {req.error_message}")

            forecast = req.get_forecast(coordinates, api_key)
            if req.has_error:
                self._display_error(
                    f"Weather forecast request failed: {req.error_message}"
                )

        return city_data, forecast

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
        if list_model != None:
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
                f"{forecast_json['list'][i]['main']['temp'] - 273.15:.0f}",
                forecast_json["list"][i]["weather"][0]["id"],
            ]
            for i in range(Constants.FORECAST_CNT)
        ]
        return forecast

    def _get_forecast_label(self, city_data):
        if "name" in city_data:
            return f"\nEnnuste paikkakunnalle {city_data['name']}:"
        return ""

    def _display_weather_data(self, city_data, forecast_data):
        station = self._data_model.current_station
        self.forecast_label.setText("")

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

        present_weather = station.get_present_weather()
        if present_weather[1] != "":
            tmp = QApplication.translate("WeatherApp", present_weather[0])
            self.present_weather_label.setText(tmp)
            self.present_weather_value.setText(
                f"{present_weather[1]}, suht. kosteus {station.air_humidity:.0f}%"
            )

        self.visibility_value.setText(station.visibility_str)

        if bool(city_data):
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

            label = QApplication.translate("WeatherApp", "Ennuste paikkakunnalle")
            if "name" in city_data:
                label += f" {city_data['name']}:"
            self.forecast_label.setText(label)

        if bool(forecast_data):
            forecast = self._get_3h_forecast(forecast_data)
            for i in range(Constants.FORECAST_CNT):
                self.weather_symbols[i + 1]["label"].setText(
                    f"{forecast[i][0]}\n{forecast[i][1]} °C"
                )
                self.weather_symbols[i + 1]["symbol"].setText(
                    f"{WeatherUtils.get_weather_symbol(forecast[i][2])}"
                )

        if not self.settings["openweathermap_api_key"]:
            self.error_message.setText("Open Weather API key is missing")

        # calculate how long we need to wait until the next update and add some slack
        waiting_time_s = station.seconds_until_next_update
        if waiting_time_s <= 0:
            self.update_interval_s = Constants.DEFAULT_POLLING_INTERVAL_S
        else:
            self.update_interval_s = int(str(f"{waiting_time_s:.0f}"))
        self.timer.start(
            (self.update_interval_s + Constants.STATION_UPDATE_DELAY_S) * 1000
        )

        time_now = datetime.now()
        if station.seconds_until_next_update > 0:
            next_update_time = time_now + timedelta(
                0, station.seconds_until_next_update
            )
            self.update_time_value.setText(
                f"{time_now.strftime(Formats.TIME_FORMAT)} --> {next_update_time.strftime(Formats.TIME_FORMAT)}"
            )
        else:
            self.update_time_value.setText(f"{time_now.strftime(Formats.TIME_FORMAT)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec())
