# -*- coding: utf-8 -*-
import pytz
import datetime

from sqlalchemy import Column, Integer, String, DateTime, Interval, Boolean
from ...dbconfig import Base 

class APIKeyError(Exception):
    def __init__(self, message):
        self.message = message


class Program(Base):
    __tablename__ = 'programs'
    id = Column(Integer, primary_key=True)
    service = Column(String)
    channel = Column(String)
    channel_jp = Column(String)
    title = Column(String)
    info = Column(String)
    start = Column(DateTime)
    end = Column(DateTime)
    duration = Column(Interval)
    is_movie = Column(Boolean)
    is_repeat = Column(Boolean)
    is_reserved = Column(Boolean, default=False)
    is_recorded = Column(Boolean, default=False)

def dict_to_program(dic):
    program = Program()
    for attr in dic:
        setattr(program, attr, dic[attr])
    return program

def naive_to_UTC(dt):
    return dt.astimezone(tz=pytz.UTC)
