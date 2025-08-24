import sys


@staticmethod
def CheckPythonVersion():
    if not sys.version_info >= (3, 10):
        print("PyWeatherView requires Python 3.10 or later")
        print("Reason: Keyword 'match' is supported starting from version 3.10")
        return False
    return True
