"""Implements a command line interface

This is for debug purposes, the game is not meant to be playable with this
interface.
This file can be run as a script.

Classes:
    CommandLineInterface: BaseUI
        A command line interface to play the game

Functions:
    main:
        Instanciates a CLI and launches the game
"""

import argparse
import json
import selectors
import shutil
import sys
from pathlib import Path
from typing import Optional
from typing import Sequence

from boomblazer.ui.base_ui import BaseUI
from boomblazer.game_handler import MoveActionEnum
from boomblazer.map_environment import MapEnvironment
from boomblazer.version import GAME_NAME
from boomblazer.version import VERSION_STR


class CommandLineInterface(BaseUI):
    """A command line interface to play the game

    Special methods:
        __init__:
            Initiates the command line user interface

    Methods:
        main_menu:
            Creates or joins the game and go to the lobby
        play_game:
            Sends player actions and displays game state
        handle_user_input:
            Sends user input to server as player actions
        handle_network_input:
            Recieves game info from the server
    """

    __slots__ = ()

    def __init__(self, *args, **kwargs) -> None:
        """Initiates the command line user interface
        """
        super().__init__(*args, **kwargs)

    def main_menu(self, args: argparse.Namespace) -> None:
        """Creates or joins the game and go to the lobby

        Parameters:
            args: argparse.Namespace
                The arguments given through the command line.
                It must contain the following:
                    cmd: str
                        Whether to host, join, or create the game
                    address (host and join only): str
                        The address of the server
                    port: int
                        The port of the server
                    name: str
                        The player name
                    map_filename (create only): Path
                        The file containing the map data
        """
        if args.cmd == "host":
            self.join_game((args.address, args.port), args.name, is_host=True)
        elif args.cmd == "join":
            self.join_game((args.address, args.port), args.name, is_host=False)
        elif args.cmd == "create":
            self.create_game_and_join(args.port, args.name, args.map_filename)
        else:  # exit
            return
        self.play_game()

    def play_game(self) -> None:
        """Sends player actions and displays game state
        """
        if self.client.is_host:
            print('Send "start" to start the game')

        sel = selectors.DefaultSelector()
        sel.register(sys.stdin, selectors.EVENT_READ)

        while self.is_in_game:
            event = sel.select(0)  # [] if no event
            if event:
                cmd = input()
                self.handle_user_input(cmd)
            elif self.is_game_state_updated.acquire(blocking=False):
                self.handle_network_input()

    def handle_user_input(self, cmd: str) -> None:
        """Sends user input to server as player actions
        """
        if cmd == "start":
            self.client.send_start()
        elif cmd == "z":
            self.client.send_move(MoveActionEnum.MOVE_UP)
        elif cmd == "s":
            self.client.send_move(MoveActionEnum.MOVE_DOWN)
        elif cmd == "q":
            self.client.send_move(MoveActionEnum.MOVE_LEFT)
        elif cmd == "d":
            self.client.send_move(MoveActionEnum.MOVE_RIGHT)
        elif cmd == "b":
            self.client.send_plant_bomb()
        elif cmd == "quit":
            self.client.send_quit()
            self.is_in_game = False
        else:
            print("up: z ; down: s ; left: q ; right: d ; bomb: b ; quit")

    def handle_network_input(self) -> None:
        """Recieves game info from the server
        """
        if self.client.game_handler.map_environment.version == 0:
            print("Players:")
            for player in self.client.game_handler.map_environment.players:
                print(f"\t{player}")
        else:
            print("\n" * shutil.get_terminal_size().lines)
            print(self.client.game_handler.map_environment)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Instanciates a CLI and launches the game

    Parameters:
        argv: Sequence[str] | None
            If None, uses command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("--log-file", type=Path)
    parser.add_argument(
        "-V", "--version", action="version",
        version=f"{GAME_NAME} {VERSION_STR}"
    )
    subparsers = parser.add_subparsers(dest="cmd")

    parser_host = subparsers.add_parser("host")
    parser_host.add_argument("address")
    parser_host.add_argument("port", type=int)
    parser_host.add_argument("name")

    parser_join = subparsers.add_parser("join")
    parser_join.add_argument("address")
    parser_join.add_argument("port", type=int)
    parser_join.add_argument("name")

    parser_create = subparsers.add_parser("create")
    parser_create.add_argument("port", type=int)
    parser_create.add_argument("name")
    parser_create.add_argument("map_filename", type=Path)

    args = parser.parse_args(argv)

    if args.cmd is None:
        parser.error("Missing cmd argument")

    verbosity = -1 if args.quiet else args.verbose
    with CommandLineInterface(verbosity=verbosity, log_file=args.log_file) as cli:
        cli.main_menu(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
