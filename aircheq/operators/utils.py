# coding: utf-8
import time
import datetime
import logging
import collections
import os
import re
import typing

import pytz


KANJI_WEEKDAYS = ['月', '火', '水', '木', '金', '土', '日']

def parse_time(time_str: str):
    return re.search('(\d+):(\d+)', time_str).groups()


def datetime_hour_over_24(
        date: datetime.date,
        hour: int,
        minute: int
) -> datetime.datetime:

    if hour >= 24:
        hour = abs(hour - 24)
        date += datetime.timedelta(days=1)

    return datetime.datetime.combine(date, datetime.time(hour, minute))


def weekday_to_date(kanji_weekday, start_day=None):
    """
    KANJI_WEEKDAYS -> datetime.date in 7days from start_day.
    if start_day is not specified, start from datetime.now()
    """
    start_day = start_day or datetime.datetime.now()

    weekdays: dict[str, int] = dict(zip(KANJI_WEEKDAYS, range(7)))
    dates = [
        start_day + datetime.timedelta(days=days)
             for days in weekdays.values()
    ]
    for date in dates:
        if date.weekday() == weekdays[kanji_weekday]:
            return date

def datetime_to_time(dt):
def datetime_to_time(dt: datetime.datetime) -> float:
    return time.mktime(dt.timetuple())

def get_coming_weekday(wday_num):
    """
    wday_num -> datetime object coming weekday taken as argument from today.
    """
    weekdays = collections.deque(range(7))

    today = datetime.date.today()
    if today.weekday() == wday_num:
        return today + datetime.timedelta(days=7)

    weekdays.rotate(-today.weekday())
    return today + datetime.timedelta(days=weekdays.index(wday_num))


def time_intervals(
        timedelta: datetime.timedelta,
        first_time: datetime.datetime = None

) -> typing.Generator[datetime.datetime, None, None]:

    first_time = first_time or jst_now()

    yield first_time

    exec_time = first_time
    while True:
        exec_time += timedelta
        yield exec_time


def naive_to_JST(dt) -> datetime.datetime:
    tz_tokyo = pytz.timezone("Asia/Tokyo")
    if getattr(dt, "tzinfo", None) != tz_tokyo:
        return tz_tokyo.localize(dt)
    return dt


def jst_now() -> datetime.datetime:
    return datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))


def init_logger(logpath: typing.Union[str, os.PathLike], quiet=False) -> logging.Logger:
    LOG_FORMAT = logging.Formatter(
        "{asctime} - {levelname:8s} - {message}",
        style="{"
    )
    logger = logging.getLogger("aircheq")

    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(LOG_FORMAT)
    logger.addHandler(console)

    file_handler = logging.FileHandler(logpath)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(LOG_FORMAT)
    logger.addHandler(file_handler)

    return logger
