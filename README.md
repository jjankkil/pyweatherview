# pyweatherview

Tiesää / Road Weather is a desktop GUI application, written in Python, which lets the user select a weather station from the list of Finnish road weather stations, and displays the latest data from the selected station, as well as symbols for the current weather and three 3-hour forecasts. Forecast data is fetched from OpenWeather API based on the city name of the selected weather station, or weather station coordinates in case the city is not found from OpenWeather service.

The labels show in the left half of the window are localized to Finnish and English. Clicking the rightmost mouse button anywhere on the window displays a popup menu for changinh the language. For the time being, the data shown in the right side of the window has not been localized.

<img alt="Screen shot" src="./screen_shot.png" />

Weather station data is fetched from Digitraffic REST/JSON API (see https://www.digitraffic.fi/en/road-traffic/), and forecasts from OpenWeather API (see https://openweathermap.org/api). OpenWeather API requires use of an API key, which is defined in file `settings.json`. Before using the application, the used needs to get an API key and store it in settings.json. Without the key the application only shows the data from the selected road wether station.

After startup, the applications polls the API in one minute interval, and when it detects a data update, it calculates how long it needs to wait before the next update (plus some slack time). When this waiting period is over, it polls the API again for updated data. This minimizes the number of polls done to the API, which limits the number of available queries for free user accounts.

In order to run the application, Python packages PyQt6, requests and python-dateutil need to be installed, e.g.
`pip install pyqt6, requests, python-dateutil`

#### Known issues

- Waiting period calculation may get confused when a new weather station is selected from the list. This can be solved by clicking the update ("Päivitä") button.

#### Improvement ideas

- The whole application should to be refactored to better follow good SW design principles.
- Displayed data should be localized, e.g. "tuntuu kuin" --> "feels like".
- Night time weather symbols should be added.
- Weather symbols could be implemented using some other technique that Segoe UI emoji font.
- For easy installation, the application should be packaged.
