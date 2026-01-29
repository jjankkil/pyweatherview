from view import ui_helpers


def test_get_station_city():
    assert ui_helpers.get_station_city("Espoo, Nupuri vt1") == "Espoo"
    assert ui_helpers.get_station_city(None) == ""


def test_weather_symbol_and_wind_text():
    assert ui_helpers.get_weather_symbol(800) == "☀"
    assert ui_helpers.get_weather_symbol(500) == "🌧"
    assert ui_helpers.wind_direction_as_text(90).startswith("idä")


def test_format_station_name():
    assert ui_helpers.format_station_name("vt1_Espoo_Nupuri") == "Espoo, Nupuri vt1"
    assert ui_helpers.format_station_name("") == ""
