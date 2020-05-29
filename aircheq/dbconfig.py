import sys
import pathlib
import contextlib
import logging

import alembic.config
from alembic import script
from alembic.runtime import migration

from sqlalchemy import MetaData
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


from . import userconfig

config = userconfig.TomlLoader()
logger = logging.getLogger(__name__)

def check_current_head(alembic_cfg, connectable):
    """
    type: (config.Config, engine.Engine) -> bool
    """
    directory = script.ScriptDirectory.from_config(alembic_cfg)
    with connectable.begin() as connection:
        context = migration.MigrationContext.configure(connection)
        return set(context.get_current_heads()) == set(directory.get_heads())


def migrate_to_head(engine):

    current_dir = str(pathlib.PosixPath(".").absolute())
    ini_path = current_dir / pathlib.PurePosixPath("alembic.ini")

    # check that DB revision is latest 
    alembic_cfg = alembic.config.Config(str(ini_path))
    if check_current_head(alembic_cfg, engine):
        logger.debug("DB revision is up-to-date.")
        return

    # instead of "PYTHONPATH=."
    if not current_dir in sys.path:
        sys.path.append(current_dir)

    # actual migration
    logger.debug("try to upgrade DB")

    args = "-x db_url={db_url} --raiseerr upgrade head".format(
                db_url = userconfig.get_db_url()
            ).split(' ')
    alembic.config.main(args)

    logger.debug("DB revision is up-to-date.")

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

@contextlib.contextmanager
def start_session(Session, *args):
    session = Session(*args)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()



meta = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

Base = declarative_base(metadata=meta)
