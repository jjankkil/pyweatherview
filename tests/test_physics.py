from model.physics import fmi_feels_like_temperature
from definitions import Constants


def test_feels_like_valid():
    # sanity check: returns numeric for reasonable inputs
    v = fmi_feels_like_temperature(3.0, 50.0, 10.0)
    assert isinstance(v, float)


def test_feels_like_invalid_inputs():
    inv = Constants.INVALID_VALUE
    assert fmi_feels_like_temperature(inv, 50.0, 10.0) == inv
    assert fmi_feels_like_temperature(3.0, inv, 10.0) == inv
    assert fmi_feels_like_temperature(3.0, 50.0, inv) == inv
