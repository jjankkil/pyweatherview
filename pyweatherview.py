import sys
from datetime import datetime

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import constants
import utils
import weatherutils

SETTINGS_FILE_NAME = "settings.json"

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
    QLabel#present_weather_label{
        font-size: 20px;
    }
    QLabel#present_weather_value{
        font-size: 20px;
    }
    QLabel#present_weather_symbol{
        font-size: 100px;
        font-family: Segoe UI emoji;
    }
    QPushButton#get_weather_button{
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
        QApplication.instance().aboutToQuit.connect(self._cleanup)

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
        self.present_weather_label = QLabel("Säätila:", self)
        self.present_weather_value = QLabel(self)
        self.present_weather_symbol = QLabel(self)
        self.get_weather_button = QPushButton("Päivitä", self)
        self.update_time_value = QLabel(self)
        self.settings = utils.load_settings(SETTINGS_FILE_NAME)

        self.init_ui()
        self.init_data()
        self.apply_settings()

    def _cleanup(self):
        self.settings["current_station"] = self.station_list.currentText()
        data = self.settings
        utils.save_settings(SETTINGS_FILE_NAME, data)

    def apply_settings(self):
        if len(self.settings.items()) == 0:
            return

        station_name = self.settings["current_station"]
        self.station_list.setCurrentText(station_name)

    def init_ui(self):
        self.setWindowTitle("PyWeatherView")
        self.setStyleSheet(LAYOUT_STYLES)

        main_layout = QVBoxLayout()
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
        grid_layout.addWidget(self.present_weather_label, 5, 0)
        grid_layout.addWidget(self.present_weather_value, 5, 1)
        main_layout.addLayout(grid_layout)

        main_layout.addWidget(self.present_weather_symbol)
        main_layout.addWidget(self.get_weather_button)
        main_layout.addWidget(self.update_time_value)
        self.setLayout(main_layout)

        self.station_list_label.setAlignment(Qt.AlignLeft)
        self.observation_time_label.setAlignment(Qt.AlignLeft)
        self.observation_time_value.setAlignment(Qt.AlignLeft)
        self.temperature_label.setAlignment(Qt.AlignLeft)
        self.temperature_value.setAlignment(Qt.AlignLeft)
        self.avg_wind_label.setAlignment(Qt.AlignLeft)
        self.avg_wind_value.setAlignment(Qt.AlignLeft)
        self.max_wind_label.setAlignment(Qt.AlignLeft)
        self.max_wind_value.setAlignment(Qt.AlignLeft)
        self.present_weather_label.setAlignment(Qt.AlignLeft)
        self.present_weather_value.setAlignment(Qt.AlignLeft)
        self.present_weather_symbol.setAlignment(Qt.AlignCenter)
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
        self.present_weather_label.setObjectName("present_weather_label")
        self.present_weather_value.setObjectName("present_weather_value")
        self.present_weather_symbol.setObjectName("present_weather_symbol")
        self.get_weather_button.setObjectName("get_weather_button")
        self.update_time_value.setObjectName("update_time_value")

        # self.station_list.setEditable(True)
        # self.station_list.setInsertPolicy(QComboBox.InsertAlphabetically)
        self.station_list.currentIndexChanged.connect(self.update_weather)
        self.get_weather_button.clicked.connect(self.update_weather)

    def init_data(self):
        station_data = self.get_weather_stations()
        self.display_weather_stations(station_data)
        self.get_weather()

    def update_weather(self):
        response = self.get_weather()
        if response.status_code == 200:
            self.display_weather(response.json())

    def get_weather_stations(self):
        """Get a list containing all weather stations.
        Returns a JSON array of stations, or None on error.
        """
        try:
            response = requests.get(constants.STATION_LIST_URL)
            response.raise_for_status()
            json_data = response.json()
            return json_data["features"]

        except:
            self.display_error(response.text)
            return None

    def get_weather(self):
        city = self.station_list.currentText()
        if city == None:
            return None
        if city.find(",") > -1:
            city = city.split(",")[0]
        url = constants.OPENWEATHERMAP_URL.format(
            city, constants.OPENWEATHERMAP_API_KEY
        )

        try:
            response = requests.get(url)
            response.raise_for_status()
            if response.status_code == 200:
                return response
        except requests.exceptions.HTTPError as http_error:
            match response.status_code:
                case 400:
                    self.display_error("Bad request:\nPlease check your input")
                case 401:
                    self.display_error("Unauthorized:\nInvalid API key")
                case 403:
                    self.display_error("Forbidden:\nAccess is denied")
                case 404:
                    self.display_error("Not found:\nCity not found")
                case 500:
                    self.display_error("Internal Server Error:\nPlease try again later")
                case 502:
                    self.display_error("Bad Gateway:\nInvalid response from the server")
                case 503:
                    self.display_error("Service Unavailable:\nServer is down")
                case 504:
                    self.display_error("Gateway Timeout:\nNo response from the server")
                case _:
                    self.display_error(f"HTTP error occurred:\n{http_error}")
        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error:\nCheck your internet connection")
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error:\nThe request timed out")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many Redirects:\nCheck the URL")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error:\n{req_error}")
        return None

    def display_error(self, message):
        self.temperature_label.setText("")
        self.temperature_value.setText(message)

        self.present_weather_symbol.clear()
        self.present_weather_label.clear()
        self.present_weather_value.clear()

    def display_weather_stations(self, json_data):
        """Populate the station list UI component from the given JSON array"""
        self.station_list.clear()
        for station in json_data:
            station_name = station["properties"]["name"]
            if weatherutils.ok_to_add_station(station_name):
                self.station_list.addItem(
                    weatherutils.format_station_name(station_name, station["id"]),
                    station["id"],
                )
        self.station_list.model().sort(0, Qt.SortOrder.AscendingOrder)

    def display_weather(self, json_data):
        # get data from json
        temperature_c = json_data["main"]["temp"] - 273.15  # convert kelvin to celsius
        feels_like_c = json_data["main"]["feels_like"] - 273.15
        wind_speed = json_data["wind"]["speed"]
        wind_deg = json_data["wind"]["deg"]
        weather_id = json_data["weather"][0]["id"]
        present_weather = json_data["weather"][0]["description"]
        humidity = json_data["main"]["humidity"]

        # update ui components
        self.temperature_label.setText("Lämpötila:")
        self.temperature_value.setText(
            f"{temperature_c:.1f} °C, tuntuu kuin {feels_like_c:.1f} °C"
        )
        self.avg_wind_value.setText(
            f"{wind_speed:.1f} m/s, suunta {wind_deg}° {weatherutils.wind_direction_as_text(wind_deg)}"
        )
        self.present_weather_symbol.setText(weatherutils.get_weather_symbol(weather_id))
        self.present_weather_value.setText(
            f"{present_weather}, suht. kosteus {humidity}%"
        )
        self.update_time_value.setText(datetime.now().strftime("%d.%m.%Y %H:%M:%S"))


if __name__ == "__main__":
    if not utils.CheckPythonVersion():
        sys.exit()

    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
