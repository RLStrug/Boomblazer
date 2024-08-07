#!/usr/bin/env python3
"""Implements a command line interface

This is for debug purposes, the game is not meant to be playable with this
interface.
This file can be run as a script.
"""

from __future__ import annotations

import argparse
import logging
import selectors
import shutil
import sys
import typing

from ..config.cli import cli_config
from ..environment.entity.player import PlayerAction
from ..metadata import GAME_NAME
from ..network.address import Address
from ..utils.argument_parser import base_parser
from ..utils.argument_parser import handle_base_arguments
from .base_ui import BaseUI

if typing.TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any


class CommandLineInterface(BaseUI):
    """A command line interface to play the game"""

    __slots__ = ()

    def main_menu(self, args: argparse.Namespace) -> None:
        """Creates or joins the game and go to the lobby

        :param args: Arguments given through the command line. Must contain:
            * cmd: str
                Whether to join, or create the game
            * address (join only): str
                Address of the server
            * name: str
                Player name
            * map_filename (create only): pathlib.Path
                File containing the map data
        """
        if args.cmd == "join":
            self.join_game(args.address, args.name)
        elif args.cmd == "create":
            self.create_game_and_join(args.address, args.name, args.map_filename)
        else:  # exit
            return
        self.play_game()

    def play_game(self) -> None:
        """Sends player actions and displays game state"""
        print(f"Send {cli_config.ready_commands[0]} when you are ready to start")
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
        """Sends user input to server as player actions"""
        if cmd in cli_config.ready_commands:
            self.client.send_ready()
        elif cmd in cli_config.up_commands:
            self.client.send_move(PlayerAction.MOVE_UP)
        elif cmd in cli_config.down_commands:
            self.client.send_move(PlayerAction.MOVE_DOWN)
        elif cmd in cli_config.left_commands:
            self.client.send_move(PlayerAction.MOVE_LEFT)
        elif cmd in cli_config.right_commands:
            self.client.send_move(PlayerAction.MOVE_RIGHT)
        elif cmd in cli_config.bomb_commands:
            self.client.send_plant_bomb()
        elif cmd in cli_config.quit_commands:
            self.client.send_quit()
            self.client.is_game_running = False

    def handle_network_input(self) -> None:
        """Recieves game info from the server"""
        if self.client.environment.map.version == 0:
            print("Players:")
            for player, is_ready in self.client.connected_players.items():
                print(f"\t{player}", end="")
                print(" (ready)" if is_ready else "")
        else:
            print("\n" * shutil.get_terminal_size().lines)
            print(self.client.environment)


def main(argv: Sequence[str] | None = None) -> int:
    """Instanciates a CLI and launches the game

    :param argv: If None, uses command line arguments
    """
    parser = argparse.ArgumentParser(parents=[base_parser])
    subparsers = parser.add_subparsers(dest="cmd")

    parser_join = subparsers.add_parser("join")
    parser_join.add_argument("address", metavar="HOST[:PORT]", type=Address.from_string)
    parser_join.add_argument("name")

    parser_create = subparsers.add_parser("create")
    parser_create.add_argument(
        "--address", metavar="[[HOST]:[PORT]]", type=Address.from_string, default=""
    )
    parser_create.add_argument("name")
    parser_create.add_argument("map_filename")

    args = parser.parse_args(argv)

    if args.cmd is None:
        parser.error("Missing cmd argument")

    handle_base_arguments(args)
    logger = logging.getLogger(f"{GAME_NAME}.cli")
    with CommandLineInterface(logger=logger) as cli:
        cli.main_menu(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
