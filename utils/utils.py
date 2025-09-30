import ctypes
import json
from datetime import datetime
import os

import requests
from dateutil import tz

from definitions import Urls


class Utils:

    # todo: move to view
    @staticmethod
    def get_station_city(formatted_station_name) -> str:
        if formatted_station_name != None:
            if formatted_station_name.find(",") > -1:
                city = formatted_station_name.split(",")[0]
                return city

        return ""

    @staticmethod
    def timestamp_to_datetime(
        timestamp_str: str, is_local_time: bool = False
    ) -> datetime:
        if is_local_time:
            return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=tz.tzlocal()
            )
        return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=tz.tzutc()
        )
    
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
                    if "ui_language" not in settings:
                        settings["ui_language"] = ""
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
