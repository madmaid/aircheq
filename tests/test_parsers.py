import json
import pytest
import pytz
# import pytest.mark

import datetime
import inspect
import pathlib

import lxml

from aircheq.operators import parsers

def test_parser_module_has_an_variable_named_modules():
    assert hasattr(parsers, "modules")

def test_parser_an_variable_named_modules_has_only_module():
    assert all(map(inspect.ismodule, parsers.modules))

def test_parser_has_generator_named_get_programs():
    assert all(map(lambda m: inspect.isgeneratorfunction(m.get_programs), parsers.modules))

def test_comparable_programs(program_factory):
    start = datetime.datetime(2000, 1, 2, 0, 4, 0)
    dur = datetime.timedelta(minutes=1)
    left, right = program_factory([(start, dur), (start, dur)])
    assert left.is_same_with(right)

@pytest.fixture
def radiko_xml_file_single():
    with open(pathlib.Path(__file__).parent /
            pathlib.PurePath("./resources/parser/radiko/single_program.xml"), "r") as f:
        return f.read().encode("utf-8")

def test_radiko_parser_parses_xml_single(radiko_xml_file_single, tz):
    #japan = pytz.timezone("Asia/Tokyo")
    expected = {
            "service": "radiko",
            "channel": "TBS",
            "channel_jp": "TBSラジオ",
            "title": "生島ヒロシのおはよう定食・一直線",
            "duration": datetime.timedelta(minutes=90),
            "start": datetime.datetime(2018, 11, 14, 5, 00, 0, tzinfo=tz),
            "end": datetime.datetime(2018, 11, 14, 6, 30, 0, tzinfo=tz),
            "info": "テスト\ntest\n生島ヒロシ",
            "is_repeat": False,
            "is_movie": False,
    }
    assert tuple(parsers.radiko.parse_guide(radiko_xml_file_single))[0] == expected 

@pytest.fixture
def agqr_html_file_single():
    with open(pathlib.Path(__file__).parent /
            pathlib.PurePath("./resources/parser/agqr/single.html"), "r") as f:
        return f.read().encode("utf-8")

def test_agqr_parser_parses_html_single(agqr_html_file_single, tz):
    #japan = pytz.timezone("Asia/Tokyo")
    executed_year = datetime.datetime.now().year
    expected = {
            "service": "agqr",
            "channel": "agqr",
            "channel_jp": "超 A&G",
            "title": "A&G ARTIST ZONE Mia REGINAのTHE CATCH",
            "duration": datetime.timedelta(minutes=60),
            "start": datetime.datetime(executed_year, 9, 30, 6, 00, 0, tzinfo=tz),
            "end": datetime.datetime(executed_year, 9, 30, 7, 00, 0, tzinfo=tz),
            "is_repeat": True,
            "is_movie": True,

    }
    assert parsers.agqr.parse_guide(agqr_html_file_single)[0] == expected

@pytest.fixture
def nhk_api_json_file_single():
    with open(pathlib.Path(__file__).parent /
            pathlib.PurePath("./resources/parser/nhk_api/single.json"), "r") as f:
        return f.read().encode("utf-8")

def test_nhk_api_parser_parses_json_single(nhk_api_json_file_single, tz):
    _json = json.loads(nhk_api_json_file_single)
    json_program = tuple(p for p in (chan for chan in _json["list"].values()))[0][0]
    expected = parsers.model.dict_to_program({
        "service": "radiru",
        "channel": "r1",
        "channel_jp": "ＮＨＫネットラジオ第1東京",
        "title": "旭川発ラジオ深夜便▽「明日へのことば」講演会から",
        "info": "　山田朋生　▽「明日へのことば」講演会から　「増毛の海があったからこその料理人生」　フランス料理シェフ…三國清三▽誕生日の花　▽明日の予告\n山田朋生，三國清三",
        "start": datetime.datetime(2019, 9, 28, 4, 5, 0, tzinfo=tz),
        "end": datetime.datetime(2019, 9, 28, 5, 00, 3, tzinfo=tz),
        "duration": datetime.timedelta(minutes=3),
        "is_repeat": False,
        "is_movie": False,
    })
    result = parsers.nhk_api.json_to_program(json_program)
    assert result.is_same_with(expected)
