"""Defines an argument parser common to all UIs and server

Global variables:
    base_parser: argparse.ArgumentParser
        Parser for arguments that should be common to all entry points. It
        should be passed in the parents argument of each parser specific to an
        entry point

Classes:
    BaseArguments:
        The result type of handle_base_arguments

Functions:
    handle_base_arguments:
        Handles the arguments of base_parser
"""

import argparse
import logging
import pathlib
from typing import NamedTuple

from boomblazer.config import config_loader
from boomblazer.logger import create_logger
from boomblazer.version import GAME_NAME
from boomblazer.version import VERSION_STR


base_parser = argparse.ArgumentParser(add_help=False)
base_parser.add_argument("-v", "--verbose", action="count", default=0)
base_parser.add_argument("-q", "--quiet", action="store_true")
base_parser.add_argument("--log-files", action="extend", nargs="+")
base_parser.add_argument("--config-file", type=pathlib.Path)
base_parser.add_argument("--cache-file", type=pathlib.Path)
base_parser.add_argument("--data-folder", type=pathlib.Path)
base_parser.add_argument(
    "-V", "--version", action="version",
    version=f"{GAME_NAME} {VERSION_STR}"
)


class BaseArguments(NamedTuple):
    """The result type of handle_base_arguments

    Members:
        logger: logging.Logger
            The application logger
    """
    logger: logging.Logger


def handle_base_arguments(args: argparse.ArgumentParser) -> BaseArguments:
    """Handles the arguments of base_parser

    Return value: BaseArguments
        The result of the treatment of the arguments of base_parser
    """
    verbosity = -1 if args.quiet else args.verbose
    logger = create_logger(GAME_NAME, verbosity, args.log_files)
    config_loader.config_file = args.config_file
    config_loader.load_config()

    return BaseArguments(logger=logger)
