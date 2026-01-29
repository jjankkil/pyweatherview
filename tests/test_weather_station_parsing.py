from model.weather_station import WeatherStation, Sensor


def make_station_weather_json():
    return {
        "dataUpdatedTime": "1970-01-01T00:00:00Z",
        "sensorValues": [
            {
                "id": 58,
                "stationId": 1,
                "name": "NÄKYVYYS_M",
                "shortName": "VIS",
                "measuredTime": "1970-01-01T00:00:00Z",
                "value": 1234,
                "unit": "m",
            },
            {
                "id": 1,
                "stationId": 1,
                "name": "ILMA",
                "shortName": "TEMP",
                "measuredTime": "1970-01-01T00:00:00Z",
                "value": 5.5,
                "unit": "C",
            },
        ],
    }


def test_weather_station_parsing_and_accessors():
    w = WeatherStation()
    ok = w.parse(make_station_weather_json())
    assert ok is True
    # visibility should be numeric and readable
    assert w.visibility == 1234
    assert w.visibility_str.endswith("km") or w.visibility_str.endswith("m")
    # temperature accessor
    assert isinstance(w.air_temperature, int) or isinstance(w.air_temperature, float)
