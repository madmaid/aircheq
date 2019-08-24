import itertools
import io
import datetime

import lxml.etree
import requests

from ... import config
from .. import auth
from . import model


def get_stations(radiko_auth=None):
    """
    return { station id: station_name }
    """
    if radiko_auth is None:
        radiko_auth = auth.RadikoAuth()

    area_id = radiko_auth.get_area()
    url = config.RADIKO_CHANNELS_FROM_AREA_URL.format(area_id=area_id)
    raw_xml = requests.get(url)
    stations_xml = lxml.etree.fromstring(raw_xml.content)

    stations = {}
    for station in stations_xml.xpath('/stations/station'):
        name = station.xpath('./name')[0].text
        station_id = station.xpath('./id')[0].text
        stations.update({station_id: name})

    return stations

def parse_guide(guide_xml):
    parser_html = lxml.etree.HTMLParser()

    root = lxml.etree.fromstring(guide_xml)

    channel = root.xpath('//radiko/stations/station')[0].attrib['id']
    channel_jp = root.xpath('//radiko/stations/station/name')[0].text
    for prog in root.xpath('//progs/prog'):

        title = prog.xpath('./title')[0].text
        # main_title = prog.xpath('./title')[0].text
        # sub_title = prog.xpath('./sub_title')[0].text
        # title = main_title + '_' + sub_title if sub_title is not None else main_title

        # parse infomation
        info_html = prog.xpath('./info')[0].text
        broken_tree = lxml.etree.parse(io.StringIO(info_html), parser_html)

        elems = [] 
        for elem in broken_tree.iter():
            if elem.tail is not None:
                elems.append(elem.tail)

            if elem.attrib.get("href") is not None:
                elems.append(elem.attrib.get("href"))

            if elem.text is not None:
                elems.append(elem.text)
        _info = '\n'.join(elems)

        _desc = prog.xpath("./desc")[0].text
        desc = _desc if _desc is not None else ""

        _person = prog.xpath("./pfm")[0].text
        person = _person if _person is not None else ""

        info = '\n'.join((_info, desc, person,))

        # cast 
        start = datetime.datetime.strptime(prog.attrib['ft'], '%Y%m%d%H%M%S')
        duration = datetime.timedelta(seconds=int(prog.attrib['dur']))
        end = start + duration

        program = {
                'service': 'radiko',
                'channel': channel,
                'channel_jp': channel_jp,
                'title': title,
                'duration': duration,
                'start': start,
                'end': end,
                'info': info,
                'is_repeat': False,
                'is_movie': False,
                }
        yield program

def get_programs(api=config.RADIKO_WEEKLY_FROM_CHANNEL_URL):
    station_ids = get_stations()
    for station_id in station_ids:
        req = requests.get(api.format(station_id=station_id))

        for d in parse_guide(req.content):
            yield model.dict_to_program(d)

