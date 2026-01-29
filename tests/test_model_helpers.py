from model.helpers import ok_to_add_station


def test_ok_to_add_station_filters():
    assert ok_to_add_station("Espoo") is True
    assert ok_to_add_station("vt1_Espoo_Nupuri") is True
    assert ok_to_add_station("TestStation") is False
    assert ok_to_add_station("LAMID_example") is False
