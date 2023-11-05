"""
Entry point of the package

Will either start a server or a client with UI depending on arguments

Constants:
    version_text: str
        The message displayed when the user asks for the software version of
        the game
    ui_mapping: dict[str, types.Moduletype]
        Associates a string with the module containing the server otr client UI
    parser: argparse.ArgumentParser
        The command line argument parser
    args: argparse.Namespace
        The arguments parsed by parser.
        Can indicate that the user wants to display the software version of the
        game or wants to start a server or client UI
    argv_rest: list[str]
        Remaining command line arguments that will be passed to the selected
        module entry point
    program: types.Moduletype
        The selected module (server, client UI)
    ret_code: int
        Indicates success or failure of the program
"""

import argparse
import sys

from version import VERSION_STR
import server
import ui


####################
# Program metadata
####################

version_text = f"BoomBlazer {VERSION_STR}"

####################
# Mapping helper to select the client UI
####################

ui_mapping = {
    "server": server,
    "cli": ui.cli,
    "ncurses": ui.ncurses,
    "pygame": NotImplemented
}

####################
# Argument parsing
####################

parser = argparse.ArgumentParser(prog="BoomBlazer")
parser.add_argument("-V", "--version", action="version", version=version_text)
parser.add_argument("ui", choices=ui_mapping.keys(), default="ncurses")
args, argv_rest = parser.parse_known_args()

####################
# Launch game
####################

program = ui_mapping[args.ui]
if program is NotImplemented:
    raise NotImplementedError(f"{args.ui} interface has yet to be implemented")

ret_code = program.main(argv_rest)

sys.exit(ret_code)
