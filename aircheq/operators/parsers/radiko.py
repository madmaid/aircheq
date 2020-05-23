import itertools
import io
import datetime

import lxml.etree
import requests

from ... import userconfig
from .. import auth
from . import model

from ..utils import naive_to_JST

config = userconfig.TomlLoader()
def parse_area_stations(stations_xml):
    """
    str -> dict { station id: station_name }
    """
    stations = dict()
    for station in stations_xml.xpath('/stations/station'):
        name = station.xpath('./name')[0].text
        station_id = station.xpath('./id')[0].text
        stations.update({station_id: name})

    return stations

def get_channels(radiko_auth=None):
    """
    return dict {"channel": "channel_jp"}
    """
    if radiko_auth is None:
        radiko_auth = auth.RadikoRTMPAuth()

    area_id = radiko_auth.get_area()
    #TODO: fetch all channels for premium
    url = config["radiko"]["channels_from_area_url"].format(area_id=area_id)
    raw_xml = requests.get(url)

    raw_xml.raise_for_status()

    return parse_area_stations(lxml.etree.fromstring(raw_xml.content))



def parse_guide(guide_xml):
    parser_html = lxml.etree.HTMLParser()

    root = lxml.etree.fromstring(guide_xml)

    channel = root.xpath('//radiko/stations/station')[0].attrib['id']
    channel_jp = root.xpath('//radiko/stations/station/name')[0].text
    for prog in root.xpath('//progs/prog'):

        title = prog.xpath('./title')[0].text
        # main_title = prog.xpath('./title')[0].text
        # sub_title = prog.xpath('./sub_title')[0].text
        # title = main_title + ' ' + (sub_title if sub_title is not None else "")

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
        _start= datetime.datetime.strptime(prog.attrib['ft'], '%Y%m%d%H%M%S')
        start = naive_to_JST(_start)
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
                # "html": info_html,
                'is_repeat': False,
                'is_movie': False,
                }
        yield program

def get_programs(api=None):
    if api is None:
        api = config["radiko"]["weekly_from_channel_url"]
    station_ids = get_channels()
    for station_id in station_ids:
        req = requests.get(api.format(station_id=station_id))
        req.raise_for_status()

        for d in parse_guide(req.content):
            yield model.dict_to_program(d)

