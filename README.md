# pyweatherview

Desktop GUI application, which lets the user select a weather station from the list of Finnish road weather stations, and displays the latest data from the selected station, as well as symbols for the current weather and 3-hour forecasts for the next 12 hours.

<img alt="Screen shot" src="./screen_shot.png" />

Weather station data is fetched from Digitraffic REST/JSON API (see https://www.digitraffic.fi/en/road-traffic/), and forecasts from OpenWeather API (see https://openweathermap.org/api). OpenWeather API requires use of an API key, which is defined in file ```settings.json```. By default a demo key created by, and belonging to, the author is used, but if the API receives too many requests for the key, it temporarily disables the key. It should be noted that the author may disable the key at any time, in which case the application displays an error message.

After startup, the applications polls the API in one minute interval, and when it detects a data update, it calculates how long it needs to wait before the next update (plus some slack time). When the waiting period is over, it polls the API again for updated data. This minimizes the number of polls done to the API, which limits the number of available queries for free user accounts.

The application has so far been developed and run only on Windows 11. On Linux there will probably be problems because of possibly missing Segoe UI emoji font used for the weather symbols.

In order to run the application, Python packages PyQt5, requests and python-dateutil need to be installed, e.g.
```pip install pyqt5, requests, python-dateutil```

#### Known issues
- Waiting period calculation may get confused when a new weather station is selected from the list. This can be solved by clicking the update ("Päivitä") button.
- Anything else, as this is (at least initially) just a learning project.

#### Improvement ideas
- The application is missing a data model and uses directly JSON objects received from the API. A data model should be created and the who code refactored and modularized accordingly.
- Weather symbols should be implemented using some other technique that Segoe UI emoji font.
- Night time weather symbols should be added.
- Localization; now all texts are hard-coded in Finnish.
- For easy installation, the application should be packaged.
