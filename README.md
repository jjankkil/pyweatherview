# README — pyweatherview

Tiesää / Road Weather is a desktop GUI application, written in Python, which lets the user select a weather station from the list of Finnish road weather stations, and displays the latest data from the selected station, as well as symbols for the current weather and three 3-hour forecasts. Forecast data is fetched from OpenWeather API based on the city name of the selected weather station, or weather station coordinates in case the city is not found from OpenWeather service.

The labels show in the left half of the window are localized to Finnish and English. Clicking the rightmost mouse button anywhere on the window displays a popup menu for changing the language. For the time being, the data shown in the right side of the window has not been localized.

<img alt="Screen shot" src="./screen_shot.png" />

Weather station data is fetched from Digitraffic REST/JSON API (see https://www.digitraffic.fi/en/road-traffic/), and forecasts from OpenWeather API (see https://openweathermap.org/api). OpenWeather API requires use of an API key, which is defined in file `settings.json`. Before using the application, the used needs to get an API key and store it in settings.json. Without the key the application only shows the data from the selected road wether station.

After startup, the applications polls the API in one minute interval, and when it detects a data update, it calculates how long it needs to wait before the next update (plus some slack time). When this waiting period is over, it polls the API again for updated data. This minimizes the number of polls done to the API, which limits the number of available queries for free user accounts.

In order to run the application, the Python packages defined in file *requirements.txt* need to be installed, e.g.
`pip install -r requirements.txt`

#### Application folder structure
- `controller/` — contains `WeatherService` (network wrapper) and `AppController` (application orchestrator).
- `model/` — domain objects and parsing (`data_model.py`, `station_info.py`, `weather_station.py`, `physics.py`, `helpers.py`).
- `view/` — UI helpers and a `NetworkWorker` to run network calls off the main thread (`ui_helpers.py`, `background_worker.py`).
- `utils/` — compatibility shims and utility functions; `web_utils.py` now centralizes HTTP calls via `RequestRunner`.

#### Testing & CI
- Tests live under `tests/` and use `pytest` with `pytest-cov` for coverage.
- A GitHub Actions workflow `/.github/workflows/ci.yml` runs the test suite and coverage on push/PR.
- Run tests locally:

```bash
pip install -r requirements.txt
python -m pytest --maxfail=1 --disable-warnings -q --cov=. --cov-report=term-missing
```

#### Notes for developers
- The UI (`pyweatherview.py`) uses `AppController` to fetch and load data; avoid direct network calls from UI code.
- Use `WeatherService` when writing non-UI code that needs network data.
- Add tests for new functionality under `tests/` and keep network calls mocked in unit tests.

#### Improvement ideas

- Displayed data should be localized, e.g. "tuntuu kuin" --> "feels like".
- Night time weather symbols should be added.
- Weather symbols could be implemented using some other technique that Segoe UI emoji font.
- For easy installation, the application should be packaged.
