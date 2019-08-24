import datetime
import pathlib

import pytz

from flask import Flask, jsonify, request, render_template
from flask.json import JSONEncoder
from sqlalchemy import or_, and_
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from .. import config
from ..operators.parsers import model
from ..operators.parsers.model import Program
from ..operators import reserve

# directory config
THIS_DIR = pathlib.PosixPath(__file__).parent
TEMPLATE_DIR = THIS_DIR.joinpath(pathlib.PurePosixPath("aircheq_wui/"))
STATIC_DIR = TEMPLATE_DIR.joinpath(pathlib.PurePosixPath("dist/"))

app = Flask('aircheq-api',
        template_folder=str(TEMPLATE_DIR),
        static_folder=str(STATIC_DIR),
        )

class ISOFormatDateTimeJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime.datetime):
                if obj.tzinfo is None:
                    obj = obj.astimezone(tz=pytz.timezone("Asia/Tokyo"))
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
app.json_encoder = ISOFormatDateTimeJSONEncoder


engine = create_engine(config.GUIDE_DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

def strip_underscore_attr(model_vars):
    return { k : v for k, v in model_vars.items() if not k.startswith("_")}

def program_to_jsondict(program):
    p = vars(program)

    p['duration'] = int(program.duration.total_seconds() * 1000)
    # exclude properties starting with "_"
    return strip_underscore_attr(p)

def strip_for_guide(program_dict):
    p = program_dict.copy()

    targets = ("end", "channel", "service", "is_recorded")
    for key in targets:
        p.pop(key)

    return p


@app.route('/', methods=['GET'])
def dashboard():
    return render_template("index.html")

@app.route('/<path:path>', methods=['GET'])
def any_root_path(path):
    return render_template("index.html")


@app.route('/api/programs.json', methods=['GET'])
def all():
    session = Session(autocommit=True)
    with session.begin(subtransactions=True):

        programs = session.query(Program).order_by(Program.id)

    session.close()
    return jsonify([ program_to_jsondict(p) for p in programs ])

@app.route('/api/guide.json', methods=['GET'])
def guide():
    session = Session(autocommit=True)
    with session.begin(subtransactions=True):
        channels = set(p.channel for p in session.query(Program).order_by(Program.service))
    session.close()

    _json = list()
    for chan in sorted(channels, key=lambda chan: chan.lower()):

        session = Session(autocommit=True)
        with session.begin(subtransactions=True):

            query = and_(Program.channel == chan, Program.end > datetime.datetime.now())
            programs = session.query(Program).filter(query).order_by(Program.start)

            if programs != []:
                name_jp = list(set(p.channel_jp for p in programs))[0]
                _json.append({
                        'name': chan,
                        'name_jp': name_jp,
                        'programs': [ program_to_jsondict(p) for p in programs ]
                })

        session.close()
    return jsonify(_json)

@app.route('/api/program_by_id.json', methods=['POST'])
def program_by_id():
    program_id = request.json.get('id', None)
    session = Session(autocommit=True)
    with session.begin(subtransactions=True):

        program = session.query(Program).filter_by(id=program_id).one()
        result = program_to_jsondict(program)

    session.close()
    return jsonify(result)

@app.route('/api/reserve.json', methods=['POST'])
def toggle_reserve():
    program_id = request.json.get('id', None)
    session = Session(autocommit=True)
    with session.begin(subtransactions=True):

        program = session.query(Program).filter_by(id=program_id).one()
        program.is_reserved = not program.is_reserved

    session.close()
    return jsonify({"res": "done"})

@app.route('/api/reserved.json', methods=['GET'])
def get_reserved():
    query = and_(Program.is_reserved==True, Program.start > datetime.datetime.now())

    session = Session(autocommit=True)
    with session.begin(subtransactions=True):

        programs = session.query(Program).filter(query)
        result = [ program_to_jsondict(p) for p in programs ]

    session.close()
    return jsonify(result)

@app.route('/api/search.json', methods=['POST'])
def search():
    PARAM_KEYS = ['id', 'service', 'channel', 'title', 'info']
    param_vals = [ request.json.get(k) for k in PARAM_KEYS ]
    params = zip(PARAM_KEYS, param_vals)

    query = and_( getattr(Program, k).contains(v) for k, v in params if v != '' )

    session = Session(autocommit=True)
    with session.begin(subtransactions=True):

        programs = session.query(Program).filter(query)
        result = [ program_to_jsondict(p) for p in programs ]

    session.close()
    return jsonify(result)

@app.route('/api/rules.json', methods=['GET'])
def fetch_rules():
    session = Session(autocommit=True)
    with session.begin(subtransactions=True):

        _rules = session.query(reserve.Rule).order_by(reserve.Rule.id)
        rules = [ strip_underscore_attr(vars(r)) for r in _rules ]

    session.close()
    return jsonify(rules)

@app.route('/api/add_rule.json', methods=['POST'])
def add_rule():
    _json = request.json

    session = Session(autocommit=True)
    with session.begin(subtransactions=True):

        rule = reserve.Rule()
        for key in _json:
            setattr(rule, key, _json[key])
        session.add(rule)

        matches = reserve.match(session, rule)
        for program in matches:
            program.is_reserved = True

    session.close()
    return jsonify({'res': 'Done'})

@app.route('/api/change_rule.json', methods=['POST'])
def change_rule():
    _json = request.json

    session = Session(autocommit=True)
    with session.begin(subtransactions=True):

        rule = session.query(reserve.Rule).filter_by(id=_json.pop("id")).one()
        for key in _json:
            setattr(rule, key, _json[key])

        matches = reserve.match(session, rule)
        for program in matches:
            program.is_reserved = True

    session.close()
    return jsonify({'res': 'Done'})

def main():
    app.run()
    return app

if __name__ == "__main__":
    main()
