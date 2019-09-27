import logging

from sqlalchemy import (Column, Integer, String, Boolean, or_, and_)
from sqlalchemy.engine import create_engine

from .parsers.model import Program
from .utils import jst_now
from .. import (config, dbconfig)
from ..dbconfig import Base 

engine = create_engine(config.GUIDE_DATABASE_URL, echo=False)
Session = dbconfig.create_session(engine)

class Rule(Base):
    __tablename__ = 'rules'
    id = Column(Integer, primary_key=True)
    service = Column(String, default='')
    channel = Column(String, default='')
    title = Column(String, default='')
    info = Column(String, default='')

    repeat = Column(Boolean, default=False)
    encode = Column(Boolean, default=False)

def str_criterion(rule):
    for attr, criteria in rule.__dict__.items():
        if type(criteria) == str and criteria != '':
            yield getattr(Program, attr).contains(criteria)

def match(session, rule):
    reserve_targets = and_(Program.end > jst_now(),
                Program.is_recording == False,
                Program.is_recorded == False)
    programs = session.query(Program).filter(reserve_targets)
    query = and_(*str_criterion(rule))

    if rule.repeat:
        return programs.filter(query)
    else:
        return programs.filter_by(is_repeat=False).filter(query)

def reserve_all():
    logger = logging.getLogger("aircheq-crawler")
    session = Session(autocommit=True)
    with session.begin():
        for rule in session.query(Rule).order_by(Rule.id):
            for program in match(session, rule):
                program.is_reserved = True
                logger.info("Reserved: {p.id} {p.channel} {p.start}".format(p=program))
    session.close()
