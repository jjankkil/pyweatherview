from model.physics import fmi_feels_like_temperature
from definitions import Constants


def test_feels_like_invalid_inputs():
    assert fmi_feels_like_temperature(Constants.INVALID_VALUE, 50, 10) == Constants.INVALID_VALUE
    assert fmi_feels_like_temperature(5, Constants.INVALID_VALUE, 10) == Constants.INVALID_VALUE
    assert fmi_feels_like_temperature(5, 50, Constants.INVALID_VALUE) == Constants.INVALID_VALUE


def test_feels_like_low_temperature():
    # temp below simmer limit should still compute a numeric result
    res = fmi_feels_like_temperature(3.0, 50.0, 10.0)
    assert isinstance(res, float)
    assert res != Constants.INVALID_VALUE
