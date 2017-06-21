import logging

from sqlalchemy import Column, Integer, String, Boolean, or_, and_
from sqlalchemy.ext.declarative import declarative_base

from .parsers.model import Program

Base = declarative_base()

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
    query = session.query(Program)
    new_query = and_(*str_criterion(rule))

    if rule.repeat:
        return query.filter(new_query)
    else:
        return query.filter_by(is_repeat=False).filter(new_query)

def reserve_all(Session):
    logger = logging.getLogger("aircheq-crawler")
    session = Session(autocommit=True)
    with session.begin():
        for rule in session.query(Rule).order_by(Rule.id):
            for program in match(session, rule).all():
                program.is_reserved = True
                logger.info("Reserved: {p.id} {p.channel} {p.start}".format(p=program))
    session.close()