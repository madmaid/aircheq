import pathlib
import argparse


def create_argparser():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config-dir", type=pathlib.PosixPath, metavar='CONFIG_DIR')
    return parser
