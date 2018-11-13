import datetime

import requests
import dateutil.parser

from . import model
from ... import config

NHK_SERVICES = {
        # NHKAPI: RADIRU_STATION
        'r1': 'r1',
        'r2': 'r2',
        'r3': 'fm'
}

API = "http://api.nhk.or.jp/v2/pg/list/{area}/{service}/{date}.json?key={apikey}"

class APIKeyError(Exception):
    def __init__(self, message):
        self.message = message

def json_to_program(json_dict):

    program = model.Program()
    program.service = "radiru"
    program.channel = NHK_SERVICES[json_dict['service']['id']]
    program.channel_jp = json_dict['service']["name"] + json_dict['area']['name']
    program.title = json_dict['title']

    info = (json_dict['subtitle'], json_dict['content'], json_dict['act'])
    program.info = '\n'.join(i for i in info if i is not None)

    program.start = dateutil.parser.parse(json_dict['start_time'])
    #_start = dateutil.parser.parse(json_dict['start_time'])
    #program.start = model.naive_to_UTC(_start)
    program.end = dateutil.parser.parse(json_dict['end_time'])
    #_end = dateutil.parser.parse(json_dict['end_time'])
    #program.end = model.naive_to_UTC(_end)
    program.duration = program.end - program.start

    program.is_movie = False
    program.is_repeat = False
    return program

def get_programs(key=config.NHK_API_KEY, channels=NHK_SERVICES.keys(),
                area=config.NHK_API_AREA, api=API):

    if not key:
        raise APIKeyError("API Key is not found. Check user config")

    for channel in channels:
        today = datetime.date.today()
        for d in range(7):
            date = today + datetime.timedelta(days=d)
            params = {
                    'area': area,
                    'service': channel,
                    'date': date.strftime('%Y-%m-%d'),
                    'apikey': key
            }
            req = requests.get(api.format_map(params))

            _json = req.json()
            try:
                if _json['fault']['datail']['errorcode'] == "steps.oauth.v2.FailedToResolveAPIKey":
                    raise APIKeyError("Invalid API Key, Check user config")
            except KeyError:
                pass

            for p in _json['list'][channel]:
                yield json_to_program(p)
