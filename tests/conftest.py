import datetime

import pytz

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from aircheq.dbconfig import (Base, create_session)
from aircheq.operators.parsers.model import (
    Program,
    Channel,
    Service,
)

class TestingSession(Session):
    def commit(self):
        self.flush()
        self.expire_all()

class SessionManager(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self._create_session(app)
        if not app.testing:
            app.teardown_appcontext(self.exit_sessions)

    def _create_session(self, app, testing=False):
        self.session = sessionmaker(
            bind = create_engine(),
            class_ = TestingSession if testing else Session,
            expire_on_commit = False)

    def _exit_session(self, response_or_exc):
        self.session.remove()
        return response_or_exc

@pytest.fixture(scope="session")
def engine():
    # return create_engine("sqlite://", echo=True)
    return create_engine("sqlite://")

@pytest.yield_fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.yield_fixture(scope="function")
def Session(engine, tables):
    conn = engine.connect()
    transaction = conn.begin()
    Session = create_session(conn)
    # Session = create_session(engine, testing=True)

    yield Session 

    #conn.rollback()
    conn.close()


@pytest.fixture(scope="session")
def service():
    return Service(name="test")

@pytest.fixture(scope="session")
def channel():
    return Channel(name="test", name_jp="テスト")

@pytest.fixture(scope="function")
def persist_service_channel(Session, service, channel):
    session = Session()
    with session.begin():

        session.add(service)
        session.commit()

        _service = session.query(Service).filter_by(name=service.name).one()
        channel.service_id = _service.id
        session.add(channel)
        session.commit()

    session.close()


@pytest.fixture(scope="session")
def tz():
    return pytz.timezone("Asia/Tokyo")


@pytest.fixture
def program_factory():
    """
    [(start: datetime.datetime, dur: datetime.timedelta)] -> factory
    """
    def f(times):
        return tuple(Program.from_dict({
                "service": "test",
                "channel": "test",
                "channel_jp": "テスト",
                "start": start,
                "duration": dur,
                "end": start + dur,
                "title": "テスト",
                "info": "テスト",
                "is_movie": False,
                "is_repeat": False,
                "is_reserved": False,
                "is_manual_reserved": False,
                "is_recording": False,
                "is_recorded": False,
        }) for start, dur in times)
    return f

