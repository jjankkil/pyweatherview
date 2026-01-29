def ok_to_add_station(raw_name: str) -> bool:
    """Return True if a station should be included in lists (filters out test/temporary stations)."""
    station_name_filter_list = [
        "Test",
        "LA",
        "TSA",
        "TEST",
        "Meteo",
        "LAMID",
        "OptX",
    ]

    for f in station_name_filter_list:
        if raw_name.find(f) > -1:
            return False

    return True
