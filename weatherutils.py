import sys

from PyQt5.QtWidgets import QComboBox


@staticmethod
def get_weather_symbol(weather_id):
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


@staticmethod
def wind_direction_as_text(degrees):
    result = ""

    while degrees > 360:
        degrees -= 360.0

    if (45 - 22.5) <= degrees and degrees < (45 + 22.5):
        result = "koillisesta"  # "NE"
    elif (90 - 22.5) < degrees and degrees < (90 + 22.5):
        result = "idästä"  # "E"
    elif (135 - 22.5) < degrees and degrees < (135 + 22.5):
        result = "kaakosta"  # "SE"
    elif (180 - 22.5) <= degrees and degrees < (180 + 22.5):
        result = "etelästä"  # "S"
    elif (225 - 22.5) <= degrees and degrees < (225 + 22.5):
        result = "lounaasta"  # "SW"
    elif (270 - 22.5) <= degrees and degrees < (270 + 22.5):
        result = "lännestä"  # "W"
    elif (315 - 22.5) <= degrees and degrees < (315 + 22.5):
        result = "luoteesta"  # "NW"
    else:
        result = "pohjoisesta"  # "N"

    return result


@staticmethod
def format_station_name(raw_name: str, station_id: int):
    if raw_name == None:
        return ""

    formatted_name = ""
    tokens = raw_name.split("_")
    item_cnt = len(tokens)
    if item_cnt > 3:
        formatted_name = f"{tokens[1]}, {tokens[2]} {tokens[0]} {tokens[3]}"
    elif item_cnt == 3:
        formatted_name = f"{tokens[1]}, {tokens[2]} {tokens[0]}"
    elif item_cnt == 2:
        formatted_name = f"{tokens[1]}, {tokens[0]}"
    else:
        formatted_name = raw_name
    return f"{formatted_name}::{station_id}"
