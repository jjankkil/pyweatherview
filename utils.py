import ctypes
import datetime
import json
import os
import sys
from datetime import datetime

from dateutil import tz


class Utils:

    @staticmethod
    def CheckPythonVersion():
        if not sys.version_info >= (3, 10):
            print("PyWeatherView requires Python 3.10 or later")
            print("Reason: Keyword 'match' is supported starting from version 3.10")
            return False
        return True

    @staticmethod
    def set_taskbar_icon():
        try:
            # use the application icon also as taskbar icon instead of generic Python process icon:
            myappid = "63BD6F81-EFE4-444F-8F9F-186984210EA9"  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except:
            # hoping that we end up here if not running on windows...
            pass

    @staticmethod
    def load_settings(file_name) -> dict:
        file_path = os.path.join(file_name)
        settings = json.loads("{}")

        try:
            with open(file_path, mode="r") as f:
                file_stats = os.stat(file_name)
                if file_stats.st_size > 0:
                    settings = json.load(f)
                    if "openweathermap_api_key" not in settings:
                        settings["openweathermap_api_key"] = ""
                    if "latest_stations" not in settings:
                        settings["latest_stations"] = []
        except FileNotFoundError:
            print(f"{file_path} not found!")

        return settings

    @staticmethod
    def save_settings(file_name, settings_json):
        filename = os.path.join(file_name)
        try:
            with open(filename, mode="w") as f:
                json.dump(settings_json, f)
        except:
            print(f"Failed to save settings to {filename}!")

    @staticmethod
    def calculate_seconds_until_next_update(
        latest_observation_time_ts, previous_observation_time_ts
    ) -> int:
        # all timestamps are UTC
        now_ts = datetime.now(tz.tzutc()).timestamp()
        if latest_observation_time_ts != previous_observation_time_ts:
            station_update_interval_s = (
                latest_observation_time_ts - previous_observation_time_ts
            )
            time_elapsed_s = now_ts - latest_observation_time_ts
            waiting_time_s = station_update_interval_s - time_elapsed_s

            # saturate to 10 minutes
            if waiting_time_s < 0:
                waiting_time_s = 0
            if waiting_time_s > 600:
                waiting_time_s = 600
            return waiting_time_s

        return 0
