import argparse
import datetime

import tabulate

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from .. import config
from ..operators.parsers.model import Program
from ..operators.parsers.model import Base as ProgramBase
from ..operators.reserve import Rule
from ..operators.reserve import Base as RuleBase

engine = create_engine(config.GUIDE_DATABASE_URL)
if not engine.dialect.has_table(engine, Program.__tablename__):
    ProgramBase.metadata.create_all(bind=engine)
if not engine.dialect.has_table(engine, Rule.__tablename__):
    RuleBase.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

def manual_reserve(program_id, switch=True):
    program = fetch_program_by_id(program_id)
    program.is_reserved = switch
    session.commit()

def fetch_guide():
    return session.query(Program).filter(Program.start > datetime.datetime.now()).order_by(Program.start)

def fetch_rules():
    return session.query(Rule).order_by(Rule.id)

def fetch_program_by_id(program_id):
    return session.query(Program).filter_by(id=int(program_id)).one()

def format_program(program):
    duration = "{}min".format(int(program.duration.seconds / 60))
    reserved = "reserved" if program.is_reserved else ""

    return (program.id, program.start, program.service, program.channel,
            duration, reserved, program.title)

def format_rule(rule):
    return { k: v for k, v in rule.__dict__.items() if not k.startswith("_") }

def print_table(table, peco=False, headers="keys"):
    kwargs = {"tablefmt": "plain"} if peco else {"headers": headers}
    print(tabulate.tabulate(table, **kwargs))

def print_guide(peco=False):
    programs = fetch_guide()
    print_table((format_program(p) for p in programs), peco=peco)

def print_rules(peco=False):
    #print([format_rule(rule).items() for rule in fetch_rules()])
    print_table((format_rule(r) for r in fetch_rules()),
                peco=peco,
                headers=list(Rule.__table__.columns.keys()),
                )

def print_program(program_id):
    program = fetch_program_by_id(program_id)

    for k, v in program.__dict__.items():
        print(k, ":", v)

def create_argparser():
    root_parser = argparse.ArgumentParser(description="command line interface for aircheq")
    subparsers = root_parser.add_subparsers()

    guide = subparsers.add_parser('guide', help='print programs')
    guide.add_argument('--peco', action="store_true")
    guide.set_defaults(func=print_guide)

    rules = subparsers.add_parser('rules', help="print rules")
    rules.add_argument('--peco', action="store_true")
    rules.set_defaults(func=print_rules)

    program = subparsers.add_parser('program', help='print a program with infomation')
    program.add_argument('program_id', type=str)
    program.set_defaults(func=lambda args: print_program(args.program_id))

    reserve = subparsers.add_parser('reserve', help='reserve a program')
    reserve.add_argument('program_id', type=str)
    reserve.set_defaults(func=lambda args: manual_reserve(args.program_id, True))

    unreserve = subparsers.add_parser('unreserve', help='unreserve a program')
    unreserve.add_argument('program_id', type=str)
    unreserve.set_defaults(func=lambda args: manual_reserve(args.program_id, False))

    return root_parser

if __name__ == "__main__":
    parser =  create_argparser()
    args = parser.parse_args()
    args.func(args)
