import ctypes
import json
from datetime import datetime
import os

import requests
from dateutil import tz

from definitions import Urls

from view.ui_helpers import get_station_city as _get_station_city
from view.ui_helpers import set_taskbar_icon as _set_taskbar_icon


class Utils:

    # UI helpers are now in view.ui_helpers; keep shims for backwards compatibility
    @staticmethod
    def get_station_city(formatted_station_name) -> str:
        """Return the city portion of a formatted station name.

        E.g. "Espoo, Nupuri vt1" -> "Espoo". Returns empty string when
        input is None or does not contain a comma.
        """
        return _get_station_city(formatted_station_name)

    @staticmethod
    def timestamp_to_datetime(
        timestamp_str: str, is_local_time: bool = False
    ) -> datetime:
        """Convert an ISO UTC timestamp to a timezone-aware `datetime`.

        `timestamp_str` must be in the format "%Y-%m-%dT%H:%M:%SZ". When
        `is_local_time` is True the returned datetime uses the local tzinfo,
        otherwise UTC tzinfo is applied.
        """
        if is_local_time:
            return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=tz.tzlocal()
            )
        return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=tz.tzutc()
        )
    
    @staticmethod
    def set_taskbar_icon():
        """Attempt to set a Windows taskbar app id for nicer icon grouping.

        This is a best-effort helper that silently ignores failures on
        non-Windows platforms.
        """
        try:
            _set_taskbar_icon()
        except Exception:
            pass

    @staticmethod
    def load_settings(file_name) -> dict:
        """Load settings JSON from `file_name` and return a settings dict.

        If the file is missing an empty defaults dictionary is returned and
        the function ensures expected keys exist.
        """
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
        """Persist `settings_json` to `file_name` as JSON.

        Failures are currently printed to stdout; callers may wrap this call
        to provide stronger error handling if required.
        """
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
        """Calculate how many seconds to wait until next poll based on
        the latest and previous observation timestamps.

        Values are UTC timestamps. The returned value is saturated to
        [0, 600] seconds.
        """
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
