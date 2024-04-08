"""Defines an argument parser common to all UIs and server
"""

import argparse
import pathlib

from boomblazer.version import GAME_NAME
from boomblazer.version import VERSION_STR

base_parser = argparse.ArgumentParser(add_help=False)
base_parser.add_argument("-v", "--verbose", action="count", default=0)
base_parser.add_argument("-q", "--quiet", action="store_true")
base_parser.add_argument("--log-file", type=pathlib.Path)
base_parser.add_argument(
    "-V", "--version", action="version",
    version=f"{GAME_NAME} {VERSION_STR}"
)
