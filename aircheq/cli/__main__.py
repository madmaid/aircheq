import argparse
import datetime
import logging
import pathlib

import tabulate
import toml

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from .. import userconfig
from ..args import create_argparser as create_rootparser
try:
    from ..operators.parsers.model import Program
    from ..operators.parsers.model import Base as ProgramBase
    from ..operators.reserve import Rule
    from ..operators.reserve import Base as RuleBase
except userconfig.LoadingConfigFailedError:
    pass

config = userconfig.TomlLoader()
logger = logging.getLogger(__name__)

def manual_reserve(session, program_id, switch=True):
    program = fetch_program_by_id(program_id)
    program.is_reserved = switch
    session.commit()

def fetch_guide(session):
    return session.query(Program).filter(Program.start > datetime.datetime.now()).order_by(Program.start)

def fetch_reserved(session):
    return session.query(Program).filter(Program.is_reserved == True).order_by(Program.start)

def fetch_rules(session):
    return session.query(Rule).order_by(Rule.id)

def fetch_program_by_id(session, program_id):
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

def print_guide(session, peco=False):
    programs = fetch_guide(session)
    print_table((format_program(p) for p in programs), peco=peco)

def print_rules(session, peco=False):
    print_table((format_rule(r) for r in fetch_rules(session)),
                peco=peco,
                headers=list(Rule.__table__.columns.keys()),
    )
def print_reserved(session, peco=False):
    programs = fetch_reserved(session)
    print_table((format_program(p) for p in programs), peco=peco)

def print_program(session, program_id):
    program = fetch_program_by_id(session, program_id)

    for k, v in program.__dict__.items():
        print(k, ":", v)

def migrate_to_toml(srcpath, dstpath):
    d = dict()
    with open(pathlib.Path(srcpath).absolute(), "r") as old:
        exec(old.read(), dict(), d)

    skel = toml.load(pathlib.Path(__file__).joinpath("../../../config.toml.skel").resolve())

    skel["general"]["recorded_dir"] = d.get("RECORDED_DIR", "~/")
    skel["radiko"]["tools_dir"] = d.get("RADIKO_TOOLS_DIR", "")
    skel["radiru"]["area"] = d.get("NHK_API_AREA", 130)
    skel["radiru"]["api_key"] = d.get("NHK_API_KEY", "")

    db_dialect, db_path = d.get("GUIDE_DATABASE_URL", "").split(":///")
    skel["db"]["guide_dialect"] = db_dialect
    skel["db"]["guide_path"] = db_path

    dst = dstpath.joinpath("config.toml") if dstpath.is_dir() else dstpath

    if dst.exists():
        confirmation = input(f"{dst} already exists. Overwrite it? (y/N):")
        if confirmation != "y":
            print ("aborted.")
            return
        
    with dst.open(mode='w') as f:
        toml.dump(skel, f, encoder=toml.TomlPathlibEncoder())


def create_argparser():
    root_parser = create_rootparser()
    root_parser.description = "command line interface for aircheq"

    subparsers = root_parser.add_subparsers()

    guide = subparsers.add_parser('guide', help='print programs')
    guide.add_argument('--peco', action="store_true")
    guide.set_defaults(func=lambda args: print_guide(session))

    rules = subparsers.add_parser('rules', help="print rules")
    rules.add_argument('--peco', action="store_true")
    rules.set_defaults(func=lambda args: print_rules(session))

    program = subparsers.add_parser('program', help='print a program with infomation')
    program.add_argument('program_id', type=str)
    program.set_defaults(func=lambda args: print_program(session, args.program_id))

    reserve = subparsers.add_parser('reserve', help='reserve a program')
    reserve.add_argument('program_id', type=str)
    reserve.set_defaults(func=lambda args: manual_reserve(session, args.program_id, True))

    unreserve = subparsers.add_parser('unreserve', help='cancel reservation')
    unreserve.add_argument('program_id', type=str)
    unreserve.set_defaults(func=lambda args: manual_reserve(session, args.program_id, False))

    reserved = subparsers.add_parser('reserved', help='print reserved programs')
    reserved.add_argument('--peco', action="store_true")
    reserved.set_defaults(func=lambda args: print_reserved(session))


    migrate_config = subparsers.add_parser("migrate-config", help="migrate config.py to toml")
    migrate_config.add_argument('srcpath', type=pathlib.Path)
    migrate_config.add_argument('dstpath', type=pathlib.Path)

    migrate_config.set_defaults(
            func=lambda args: migrate_to_toml(args.srcpath, args.dstpath),
            srcpath=userconfig.CONFIG_DIR.joinpath("config.py"),
            dstpath=userconfig.CONFIG_DIR,
    )

    return root_parser

if __name__ == "__main__":
    parser = create_argparser()
    args = parser.parse_args()
    try:
        engine = create_engine(userconfig.get_db_url())
        if not engine.dialect.has_table(engine, Program.__tablename__):
            ProgramBase.metadata.create_all(bind=engine)
        if not engine.dialect.has_table(engine, Rule.__tablename__):
            RuleBase.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
    except userconfig.LoadingConfigFailedError:
        logger.warning("you need migrate userconfig to run operator.")
    except FileNotFoundError as e:
        logger.warning("user-config is not found")
    except AttributeError as e:
        logger.warning("DB URL is not found in user-config")
    parser = create_argparser(session)
    args = parser.parse_args()


    try:
        args.func(args)
    except AttributeError:
        parser.print_usage()

