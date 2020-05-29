import logging

from sqlalchemy import (Column, Integer, String, Boolean, or_, and_)
from sqlalchemy.engine import create_engine

from .parsers.model import Program
from .utils import jst_now
from .. import userconfig
from ..dbconfig import (Base, create_session, start_session)

engine = create_engine(userconfig.get_db_url(), echo=False)
Session = create_session(engine)
logger = logging.getLogger(__name__)

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
    with start_session(Session) as session:
        for rule in session.query(Rule).order_by(Rule.id):
            for program in match(session, rule):
                program.is_reserved = True
                logger.info("Reserved: {p.id} {p.channel} {p.start}".format(p=program))
