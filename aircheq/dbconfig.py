from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

class TestingSession(Session):
    def commit(self):
        self.flush
        self.expire_all()

    def remove(self):
        self.expire_all()

def create_session(engine, testing=False):
    return sessionmaker(
        bind=engine,
        class_=TestingSession if testing else Session,
        expire_on_commit=False
    )

meta = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

Base = declarative_base(metadata=meta)
