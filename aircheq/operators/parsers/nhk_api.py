import datetime

import requests
import dateutil.parser

from ... import config
from . import model

NHK_NETRADIO_TO_SERVICES = {
        # NHKAPI: RADIRU_STATION
        'n1': 'r1',
        'n2': 'r2',
        'n3': 'fm'
}


def program_api(date):
    api = config.NHK_API_URL
    key = config.NHK_API_KEY
    area = config.NHK_API_AREA
    params = {
            'area': area,
            'service': "netradio",
            'date': date.strftime('%Y-%m-%d'),
            'apikey': key
    }
    req = requests.get(api.format_map(params))

    if req.status_code == 401:
        raise model.APIKeyError("Invalid API Key, Check a paramater: NHK_API_KEY in your config")
    req.raise_for_status()

    return req.json()

def parse_channel(json_dict):
    """
    partial_json_dict -> {"channel": "channel_jp"}
    """

    channel = NHK_NETRADIO_TO_SERVICES[json_dict['service']['id']]
    channel_jp = json_dict['service']["name"] + json_dict['area']['name']
    return { channel: channel_jp }


def get_channels():
    """
    return {"channel": "channel_jp"}
    """
    _json = program_api(datetime.date.today())

    channels = dict()
    for programs in _json['list'].values():
        # take first program in each channels from guide
        channels.update(parse_channel(programs[0]))

    return channels


def json_to_program(json_dict):

    program = model.Program()
    program.service = "radiru"
    program.channel = NHK_NETRADIO_TO_SERVICES[json_dict['service']['id']]
    program.channel_jp = json_dict['service']["name"] + json_dict['area']['name']
    program.title = json_dict['title']

    info = (json_dict['subtitle'], json_dict['content'], json_dict['act'])
    program.info = '\n'.join(i for i in info if i is not None)

    program.start = dateutil.parser.parse(json_dict['start_time'])
    program.end = dateutil.parser.parse(json_dict['end_time'])
    program.duration = program.end - program.start

    program.is_movie = False
    program.is_repeat = False
    return program


def get_programs():
    today = datetime.date.today()
    for dayafter in range(7):
        date = today + datetime.timedelta(days=dayafter)
        _json = program_api(date)

        for ch in _json["list"].values():
            for program in ch:
                yield json_to_program(program)

