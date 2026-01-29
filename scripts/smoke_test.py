"""Automated smoke tests for pyweatherview.

Run from repository root: `python scripts\smoke_test.py`
"""
import sys, os
# ensure project root is on sys.path when running this script directly
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from controller.app_controller import AppController
from utils.utils import Utils
import json


def run_checks():
    print("Starting programmatic smoke tests")
    ctl = AppController()
    print("Fetching station list...")
    success = ctl.fetch_and_load_station_list()
    print("fetch_and_load_station_list ->", success)
    stations = ctl.get_stations()
    print("Station count =", len(stations))

    if len(stations) > 0:
        st = stations[0]
        print("First station id, name =", st.id, getattr(st, "formatted_name", None))
        sid = st.id
        print("Fetching station data for id", sid)
        ok = ctl.fetch_and_load_station_data(sid)
        print("fetch_and_load_station_data ->", ok)
        cs = ctl.get_current_station()
        print("Current station id =", cs.id)

        settings = Utils.load_settings("settings.json")
        api_key = settings.get("openweathermap_api_key", "")
        coords = cs.coordinates
        city = Utils.get_station_city(getattr(cs, "formatted_name", ""))
        print("Using API key present:", bool(api_key))
        if api_key:
            city_data = ctl.service.get_city_weather(city, coords, api_key)
            if isinstance(city_data, dict):
                print("city_data keys:", list(city_data.keys()))
            else:
                print("city_data type:", type(city_data))

            forecast = ctl.service.get_forecast(coords, api_key)
            if isinstance(forecast, dict):
                print("forecast keys:", list(forecast.keys()))
            else:
                print("forecast type:", type(forecast))


if __name__ == "__main__":
    run_checks()
