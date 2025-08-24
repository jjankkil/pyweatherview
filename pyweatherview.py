# import json
import sys

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QWidget,
)

import utils
import weatherutils

LAYOUT_STYLES = """
    QLabel, QPushButton{
        font-family: calibri;
    }
    QComboBox#station_list{
        font-size: 20px;
    }
    QPushButton#get_weather_button{
        font-size: 20px;
        font-weight: bold;
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
    QLabel#symbol_label{
        font-size: 100px;
        font-family: Segoe UI emoji;
    }
    QLabel#present_weather_label{
        font-size: 20px;
    }
    QLabel#present_weather_value{
        font-size: 20px;
    }
"""


class WeatherApp(QWidget):

    def __init__(self):
        super().__init__()
        self.station_list = QComboBox(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel("Lämpötila:", self)
        self.temperature_value = QLabel(self)
        self.avg_wind_label = QLabel("Keskituuli:", self)
        self.avg_wind_value = QLabel(self)
        self.symbol_label = QLabel(self)
        self.present_weather_label = QLabel("Säätila:", self)
        self.present_weather_value = QLabel(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("PyWeatherView")
        self.setStyleSheet(LAYOUT_STYLES)

        layout = QGridLayout()
        layout.addWidget(self.station_list, 0, 0)
        layout.addWidget(self.get_weather_button, 0, 1)
        layout.addWidget(self.temperature_label, 2, 0)
        layout.addWidget(self.temperature_value, 2, 1)
        layout.addWidget(self.avg_wind_label, 3, 0)
        layout.addWidget(self.avg_wind_value, 3, 1)
        layout.addWidget(self.present_weather_label, 4, 0)
        layout.addWidget(self.present_weather_value, 4, 1)
        layout.addWidget(self.symbol_label, 5, 1)
        self.setLayout(layout)

        self.temperature_label.setAlignment(Qt.AlignLeft)
        self.temperature_value.setAlignment(Qt.AlignLeft)
        self.avg_wind_label.setAlignment(Qt.AlignLeft)
        self.avg_wind_value.setAlignment(Qt.AlignLeft)
        self.symbol_label.setAlignment(Qt.AlignLeft)
        self.present_weather_label.setAlignment(Qt.AlignLeft)
        self.present_weather_value.setAlignment(Qt.AlignLeft)

        self.station_list.setObjectName("station_list")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.temperature_value.setObjectName("temperature_value")
        self.avg_wind_label.setObjectName("avg_wind_label")
        self.avg_wind_value.setObjectName("avg_wind_value")
        self.symbol_label.setObjectName("symbol_label")
        self.present_weather_label.setObjectName("present_weather_label")
        self.present_weather_value.setObjectName("present_weather_value")

        weatherutils.get_weather_stations(self.station_list)
        self.get_weather_button.clicked.connect(self.get_weather)

    def get_weather(self):
        api_key = ""  # Replace with your OpenWeatherMap API key
        city = self.station_list.currentText()
        url = (
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        )

        try:
            response = requests.get(url)
            response.raise_for_status()
            # print(response.text)
            data = response.json()
            if data["cod"] == 200:
                self.display_weather(data)
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

    def display_error(self, message):
        self.temperature_label.setText("")
        self.temperature_value.setText(message)

        self.symbol_label.clear()
        self.description_label.clear()

    def display_weather(self, data):
        # get data from json
        temperature_c = data["main"]["temp"] - 273.15  # convert kelvin to celsius
        feels_like_c = data["main"]["feels_like"] - 273.15
        wind_speed = data["wind"]["speed"]
        wind_deg = data["wind"]["deg"]

        weather_id = data["weather"][0]["id"]
        present_weather = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]

        # update ui components
        self.temperature_label.setText("Lämpötila:")
        self.temperature_value.setText(
            f"{temperature_c:.1f} °C, tuntuu kuin {feels_like_c:.1f} °C"
        )
        self.avg_wind_value.setText(
            f"{wind_speed:.1f} m/s, suunta {wind_deg}° {weatherutils.wind_direction_as_text(wind_deg)}"
        )
        self.symbol_label.setText(weatherutils.get_weather_symbol(weather_id))
        self.present_weather_value.setText(
            f"{present_weather}, suht. kosteus {humidity}%"
        )


if __name__ == "__main__":
    if not utils.CheckPythonVersion():
        sys.exit()

    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
