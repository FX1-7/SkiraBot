import datetime as dt


def utc_now():
    return dt.datetime.now(dt.timezone.utc)
