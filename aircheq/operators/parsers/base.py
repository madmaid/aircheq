from typing import TypedDict
from datetime import timedelta, datetime
from dataclasses import dataclass

from ..utils import naive_to_JST
from ... import userconfig

@dataclass
class APIKeyError(Exception):
    message: str


@dataclass
class GuideParser:
    config: userconfig.ConfigLoader


class ProgramDict(TypedDict):
    service: str
    channel: str
    channel_jp: str
    title: str
    duration: timedelta
    start: datetime
    end: datetime
    info: str
    is_repeat: bool
    is_movie: bool

