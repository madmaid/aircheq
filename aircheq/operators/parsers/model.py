# -*- coding: utf-8 -*-
import pytz
import datetime

from sqlalchemy import (
        Column, Integer, String, DateTime, Interval, Boolean,
        ForeignKey
)
from sqlalchemy.orm import relationship

from ...dbconfig import Base
from ..utils import (naive_to_JST)



class Program(Base):
    __tablename__ = 'programs'
    id = Column(Integer, primary_key=True)

    service = Column(String)
    channel = Column(String)
    channel_jp = Column(String)

    service_id = Column(Integer, ForeignKey("services.id"))
    service_entity = relationship("Service")

    channel_id = Column(Integer, ForeignKey("channels.id"))
    channel_entity = relationship("Channel")

    title = Column(String)
    info = Column(String)
    # html = Column(String, nullable=True)

    # casts = Column(String, nullable=True)

    start = Column(DateTime(timezone=True))
    end = Column(DateTime(timezone=True))
    duration = Column(Interval)
    is_movie = Column(Boolean)
    is_repeat = Column(Boolean)
    is_reserved = Column(Boolean, default=False)
    is_recorded = Column(Boolean, default=False)
    is_recording = Column(Boolean, default=False)
    is_manual_reserved = Column(Boolean, default=False)

    @classmethod
    def from_dict(cls, dic):
        program = cls()
        for k,v in dic.items():
            setattr(program, k, v)
        return program

    def is_same_with(self, the_other):
        return is_same_program(self, the_other)

def is_same_program(program_a, program_b):
    attributes = ("service", "channel", "start", "end", "title")
    for attr in attributes:
        targets = getattr(program_a, attr), getattr(program_b, attr)

        if all(type(t) == datetime.datetime for t in targets):
            left, right = tuple(naive_to_JST(t) if t.tzinfo is None else t for t in targets)
        else:
            left, right = targets

        if left != right:
            return False

    return True
        
def dict_to_program(dic):
    program = Program()
    for k, v in dic.items():
        setattr(program, k, v)
    return program

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    channels = relationship("Channel", backref="services")

class Channel(Base):
    __tablename__ = "channels"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    name_jp = Column(String, nullable=False)
    # area = Column(String, nullable=True)

    service_id = Column(Integer, ForeignKey("services.id"))
    service = relationship("Service")


