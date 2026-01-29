import ctypes

from datetime import datetime
from dateutil import tz


def get_station_city(formatted_station_name) -> str:
    if formatted_station_name is not None:
        if formatted_station_name.find(",") > -1:
            city = formatted_station_name.split(",")[0]
            return city

    return ""


def set_taskbar_icon():
    try:
        myappid = "63BD6F81-EFE4-444F-8F9F-186984210EA9"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        # non-windows platforms or failure are silently ignored
        pass


def get_weather_symbol(weather_id):
    # same mapping as original utils/weather_utils
    if 200 <= weather_id <= 232:
        return "⛈"
    elif 300 <= weather_id <= 321:
        return "🌦"
    elif 500 <= weather_id <= 531:
        return "🌧"
    elif 600 <= weather_id <= 622:
        return "❄"
    elif 701 <= weather_id <= 741:
        return "🌫"
    elif weather_id == 762:
        return "🌋"
    elif weather_id == 771:
        return "💨"
    elif weather_id == 781:
        return "🌪"
    elif weather_id == 800:
        return "☀"
    elif 801 <= weather_id <= 804:
        return "☁"
    else:
        return ""


def wind_direction_as_text(degrees):
    if degrees is None:
        return ""

    while degrees > 360:
        degrees -= 360.0

    if (45 - 22.5) <= degrees and degrees < (45 + 22.5):
        return "koillisesta"
    elif (90 - 22.5) < degrees and degrees < (90 + 22.5):
        return "idästä"
    elif (135 - 22.5) < degrees and degrees < (135 + 22.5):
        return "kaakosta"
    elif (180 - 22.5) <= degrees and degrees < (180 + 22.5):
        return "etelästä"
    elif (225 - 22.5) <= degrees and degrees < (225 + 22.5):
        return "lounaasta"
    elif (270 - 22.5) <= degrees and degrees < (270 + 22.5):
        return "lännestä"
    elif (315 - 22.5) <= degrees and degrees < (315 + 22.5):
        return "luoteesta"
    else:
        return "pohjoisesta"


def format_station_name(raw_name: str) -> str:
    if raw_name is None or raw_name == "":
        return ""

    tokens = raw_name.split("_")
    item_cnt = len(tokens)

    if item_cnt > 3:
        return f"{tokens[1]}, {tokens[2]} {tokens[0]} {tokens[3]}"
    elif item_cnt == 3:
        return f"{tokens[1]}, {tokens[2]} {tokens[0]}"
    elif item_cnt == 2:
        return f"{tokens[1]}, {tokens[0]}"
    else:
        return raw_name
