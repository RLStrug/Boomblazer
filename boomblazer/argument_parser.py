"""Defines an argument parser common to all UIs and server

Global variables:
    base_parser: argparse.ArgumentParser
        Parser for arguments that should be common to all entry points. It
        should be passed in the parents argument of each parser specific to an
        entry point

Functions:
    handle_base_arguments:
        Handles the arguments of base_parser
"""

import argparse
import pathlib

from boomblazer.config import config_loader
from boomblazer.logging import logger
from boomblazer.version import GAME_NAME
from boomblazer.version import VERSION_STR


base_parser = argparse.ArgumentParser(add_help=False)
base_parser.add_argument("--config-file", type=pathlib.Path)
base_parser.add_argument(
    "-V", "--version", action="version",
    version=f"{GAME_NAME} {VERSION_STR}"
)


def handle_base_arguments(args: argparse.ArgumentParser) -> None:
    """Handles the arguments of base_parser

    Return value: BaseArguments
        The result of the treatment of the arguments of base_parser
    """
    config_loader.config_file = args.config_file
    config_loader.load_config()

    logger.setup()
