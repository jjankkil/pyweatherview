import json
import os
import sys


@staticmethod
def CheckPythonVersion():
    if not sys.version_info >= (3, 10):
        print("PyWeatherView requires Python 3.10 or later")
        print("Reason: Keyword 'match' is supported starting from version 3.10")
        return False
    return True


@staticmethod
def load_settings(file_name) -> dict:
    file_path = os.path.join(file_name)
    settings = json.loads("{}")

    try:
        with open(file_path, mode="r") as f:
            file_stats = os.stat(file_name)
            if file_stats.st_size > 0:
                settings = json.load(f)
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
