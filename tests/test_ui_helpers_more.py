from view.ui_helpers import (
    get_weather_symbol,
    wind_direction_as_text,
    format_station_name,
    get_station_city,
)


def test_weather_symbol_boundaries():
    assert get_weather_symbol(200) == "⛈"
    assert get_weather_symbol(232) == "⛈"
    assert get_weather_symbol(300) == "🌦"
    assert get_weather_symbol(500) == "🌧"
    assert get_weather_symbol(600) == "❄"
    assert get_weather_symbol(701) == "🌫"
    assert get_weather_symbol(762) == "🌋"
    assert get_weather_symbol(771) == "💨"
    assert get_weather_symbol(781) == "🌪"
    assert get_weather_symbol(800) == "☀"
    assert get_weather_symbol(802) == "☁"
    assert get_weather_symbol(9999) == ""


def test_wind_direction_and_wrapping():
    assert wind_direction_as_text(None) == ""
    assert wind_direction_as_text(370) == wind_direction_as_text(10)
    assert wind_direction_as_text(45) == "koillisesta"
    assert wind_direction_as_text(180) == "etelästä"


def test_format_station_name_and_city():
    assert format_station_name(None) == ""
    assert format_station_name("") == ""
    assert format_station_name("VT1_Nupuri_Espoo_1") == "Nupuri, Espoo VT1 1"
    assert format_station_name("VT1_Nupuri_Espoo") == "Nupuri, Espoo VT1"
    assert format_station_name("VT1_Nupuri") == "Nupuri, VT1"
    assert get_station_city("Espoo, Nupuri vt1") == "Espoo"
