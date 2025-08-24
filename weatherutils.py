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
def get_weather_stations(station_list: QComboBox):
    station_list.addItem("Oulu, Ritaharju VT4")
    station_list.addItem("Vantaa, Keimola VT3")
    return station_list.count()


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
