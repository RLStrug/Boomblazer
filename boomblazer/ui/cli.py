#!/usr/bin/env python3
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
import selectors
import shutil
import sys
from pathlib import Path
from typing import Optional
from typing import Sequence

from boomblazer.argument_parser import base_parser
from boomblazer.argument_parser import handle_base_arguments
from boomblazer.config.cli import cli_config
from boomblazer.ui.base_ui import BaseUI
from boomblazer.game_handler import MoveActionEnum


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
                        Whether to join, or create the game
                    address (join only): str
                        The address of the server
                    port: int
                        The port of the server
                    name: str
                        The player name
                    map_filename (create only): Path
                        The file containing the map data
        """
        if args.cmd == "join":
            self.join_game((args.address, args.port), args.name)
        elif args.cmd == "create":
            self.create_game_and_join(args.port, args.name, args.map_filename)
        else:  # exit
            return
        self.play_game()

    def play_game(self) -> None:
        """Sends player actions and displays game state
        """
        print(
            f'Send "{cli_config.ready_commands[0]}" when you are ready '
            'to start the game.'
        )
        print("The game will start when all players are ready")
        print(
            f"up: {cli_config.up_commands[0]} ; "
            f"down: {cli_config.down_commands[0]} ; "
            f"left: {cli_config.left_commands[0]} ; "
            f"right: {cli_config.right_commands[0]} ; "
            f"bomb: {cli_config.bomb_commands[0]} ; "
            f"quit: {cli_config.quit_commands[0]}"
        )

        sel = selectors.DefaultSelector()
        sel.register(sys.stdin, selectors.EVENT_READ)

        while self.client.is_game_running:
            event = sel.select(0)  # [] if no event
            if event:
                cmd = input()
                self.handle_user_input(cmd)
            elif self.client.update_semaphore.acquire(blocking=False):
                self.handle_network_input()

    def handle_user_input(self, cmd: str) -> None:
        """Sends user input to server as player actions
        """
        if cmd in cli_config.ready_commands:
            self.client.send_ready()
        elif cmd in cli_config.up_commands:
            self.client.send_move(MoveActionEnum.MOVE_UP)
        elif cmd in cli_config.down_commands:
            self.client.send_move(MoveActionEnum.MOVE_DOWN)
        elif cmd in cli_config.left_commands:
            self.client.send_move(MoveActionEnum.MOVE_LEFT)
        elif cmd in cli_config.right_commands:
            self.client.send_move(MoveActionEnum.MOVE_RIGHT)
        elif cmd in cli_config.bomb_commands:
            self.client.send_plant_bomb()
        elif cmd in cli_config.quit_commands:
            self.client.send_quit()
            self.client.is_game_running = False

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
    parser = argparse.ArgumentParser(parents=[base_parser])
    subparsers = parser.add_subparsers(dest="cmd")

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

    base_args = handle_base_arguments(args)
    with CommandLineInterface(logger=base_args.logger) as cli:
        cli.main_menu(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
