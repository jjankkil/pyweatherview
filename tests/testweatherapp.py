import json
import unittest
from unittest.mock import MagicMock, patch

from PyQt6.QtWidgets import QApplication

from model import data_model
from pyweatherview import WeatherApp
from utils import Utils
from weatherutils import WeatherUtils


class TestWeatherApp(unittest.TestCase):
    @staticmethod
    def load_json_from_file(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def setUpClass(cls):
        # Create a QApplication instance for testing PyQt6 widgets
        cls.app = QApplication([])

    def setUp(self):
        # Initialize the WeatherApp for each test
        self.weather_app = WeatherApp()
        self.weather_app.settings = Utils.load_settings("tests/resources/settings.json")

    def tearDown(self):
        # Clean up after each test
        self.weather_app.close()

    def test_ui_initialization(self):
        """Test that the UI components are initialized correctly."""
        self.assertIsNotNone(self.weather_app.station_list)
        self.assertIsNotNone(self.weather_app.update_button)
        self.assertTrue(self.weather_app.station_list.count() > 0)

    @patch("pyweatherview.Requestor")
    def test_get_station_list(self, MockRequestor):
        """Test that the station list is populated correctly."""
        mock_requestor = MockRequestor.return_value
        j = TestWeatherApp.load_json_from_file("tests/resources/stations.json")
        mock_requestor.get_weather_stations.return_value = j["features"]
        mock_requestor.has_error = False

        self.assertTrue(self.weather_app._get_station_list())
        self.assertEqual(len(self.weather_app._data_model.stations), 8)
        self.assertEqual(
            self.weather_app._data_model.stations[0].formatted_name, "Espoo, Nupuri vt1"
        )

    @patch("pyweatherview.Requestor")
    def test_on_station_selected(self, MockRequestor):
        """Test that weather data is fetched and displayed when a station is selected."""
        mock_requestor = MockRequestor.return_value
        mock_requestor.get_road_weather.return_value = {
            "station_id": 1,
            "dataUpdatedTime": "2025-08-19T07:11:16Z",
            "sensorValues": [
                {
                    "id": 1,
                    "stationId": 12082,
                    "name": "ILMA",
                    "shortName": "Ilma ",
                    "measuredTime": "2025-08-19T07:09:54Z",
                    "value": 13.1,
                    "unit": "°C",
                }
            ],
            "data": "mock_data",
        }
        mock_requestor.get_city_weather.return_value = {"weather": [{"id": 800}]}
        mock_requestor.get_forecast.return_value = {
            "list": [
                {"dt": 1633036800, "main": {"temp": 293.15}, "weather": [{"id": 800}]}
            ]
        }
        mock_requestor.has_error = False

        self.weather_app.station_list.setCurrentIndex(0)  # calls _on_station_selected()
        self.assertEqual(
            13.1, self.weather_app._data_model.current_station.air_temperature
        )

    def test_clear_ui_components(self):
        """Test that UI components are cleared correctly."""
        self.weather_app.temperature_value.setText("25°C")
        self.weather_app._clear_ui_components()
        self.assertEqual(self.weather_app.temperature_value.text(), "")

    def test_display_error(self):
        """Test that error messages are displayed correctly."""
        error_message = "Test error message"
        self.weather_app._display_error(error_message)
        self.assertEqual(self.weather_app.error_message.text(), error_message)

    @patch("pyweatherview.Utils.load_settings")
    def test_apply_settings(self, mock_load_settings):
        """Test that settings are applied correctly."""
        mock_load_settings.return_value = Utils.load_settings(
            "tests/resources/settings.json"
        )
        self.weather_app._apply_settings()
        self.assertEqual(
            self.weather_app.station_list.currentText(), "Espoo, Nupuri vt1"
        )

    @patch("pyweatherview.Utils.save_settings")
    def test_cleanup(self, mock_save_settings):
        """Test that settings are saved on cleanup."""
        self.weather_app.station_list.addItem("Station 1")
        self.weather_app.station_list.setCurrentIndex(0)
        self.weather_app._cleanup()
        mock_save_settings.assert_called_once()

    def test_set_ui_language(self):
        """Test that the UI language is set correctly."""
        with patch.object(QApplication, "installTranslator") as mock_install:
            self.weather_app._set_ui_language("fi-eng")
            mock_install.assert_called_once()

    def test_set_ui_labels(self):
        """Test that UI labels are updated correctly."""
        self.weather_app._set_ui_labels()
        self.assertEqual(self.weather_app.station_list_label.text(), "Havaintoasema:")

    def test_get_3h_forecast(self):
        """Test that the 3-hour forecast is parsed correctly."""
        expected_values = [
            ["12:00", 8, 800],  # time, temperature in Celsius, weather code
            ["15:00", 10, 800],
            ["18:00", 11, 802],
        ]

        forecast_json = TestWeatherApp.load_json_from_file(
            "tests/resources/forecast.json"
        )
        forecast = self.weather_app._get_3h_forecast(forecast_json)
        self.assertEqual(len(forecast), len(expected_values))

        for i in range(len(expected_values)):
            self.assertEqual(forecast[i][0], expected_values[i][0])
            self.assertEqual(forecast[i][1], expected_values[i][1])
            self.assertEqual(forecast[i][2], expected_values[i][2])

    def test_get_current_weather_id(self):
        """Test that the current weather ID is extracted correctly."""
        city_data = {"weather": [{"id": 800}]}
        weather_id = self.weather_app._get_current_weather_id(city_data)
        self.assertEqual(weather_id, 800)

    @classmethod
    def tearDownClass(cls):
        # Clean up the QApplication instance
        cls.app.quit()


if __name__ == "__main__":
    unittest.main()
