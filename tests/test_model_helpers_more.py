from model.helpers import ok_to_add_station


def test_ok_to_add_station_filters():
    assert ok_to_add_station("NormalStation") is True
    assert ok_to_add_station("TestStation") is False
    assert ok_to_add_station("MeteoStation") is False
    assert ok_to_add_station("LAMID-foo") is False
