import pytest
from pytest_mock import mocker

import datetime
from contextlib import ExitStack

import pytz

from aircheq.operators import crawler
from aircheq.operators.parsers.model import Program
from aircheq.dbconfig import start_session


def test_persist_all_programs_stores_only_future_program(mocker, program_factory, Session):
    now = datetime.datetime(2000, 1, 2, 0, 2, 0)
    start_first = datetime.datetime(2000, 1, 2, 0, 0, 0)
    start_second = datetime.datetime(2000, 1, 2, 0, 4, 0)
    dur = datetime.timedelta(minutes=1)

    programs = program_factory([(start_first, dur), (start_second, dur)])

    crawler_path = "aircheq.operators.crawler."
    with ExitStack() as stack:
        mock_session = stack.enter_context(
                mocker.patch(crawler_path + "Session", return_value=Session())
        )
        mock_now = stack.enter_context(
                mocker.patch(crawler_path + "jst_now", return_value=now)
        )
        mock_fetch_all_programs = stack.enter_context(
                mocker.patch(crawler_path + "fetch_all_programs", return_value=programs)
        )

        crawler.persist_all_programs()

        with start_session(Session) as session:
            assert programs[-1].is_same_with(session.query(Program).one())
