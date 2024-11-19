#!/usr/bin/env python3
"""Implements a command line interface

This is for debug purposes, the game is not meant to be playable with this
interface.
This file can be run as a script.
"""

from __future__ import annotations

import argparse
import logging
import shutil
import typing

from ..config.cli import cli_config
from ..environment.entity.player import PlayerAction
from ..environment.position import Position
from ..metadata import GAME_NAME
from ..network.address import Address
from ..network.client import ClientState
from ..utils.argument_parser import base_parser
from ..utils.argument_parser import handle_base_arguments
from .base_ui import BaseUI

if typing.TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any
    from ..environment.environment import Environment


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
        self.wait_in_lobby()
        self.play_game()

    def wait_in_lobby(self) -> None:
        """Waits for game to start"""
        while self.client.state is ClientState.WAITING_IN_LOBBY:
            print(
                f"spawn at (x,y) coordinates: {cli_config.spawn_commands[0]} <x> <y>",
                f"despawn: {cli_config.despawn_commands[0]} 0",
                f"ready to start: {cli_config.ready_commands[0]}",
                f"not ready to start: {cli_config.not_ready_commands[0]}",
                f"quit game: {cli_config.quit_commands[0]}",
                "The game will start when all players are ready",
                "This UI will only update after pressing ENTER",
                sep="\n",
            )

            for client_info in self.client.other_clients.values():
                print(
                    f"{client_info.name.decode('utf8')} {client_info.spawn_point}:",
                    "READY" if client_info.is_ready else "NOT READY",
                )

            cmd = input()

            if cmd in cli_config.spawn_commands:
                print(
                    f"Available spawn points: {self.client.environment.spawn_points}",
                )
                args = input("x y = ").split()

                try:
                    x = int(args[0])
                    y = int(args[1])
                except ValueError:
                    pass
                except IndexError:
                    pass
                self.client.send_spawn(Position(x, y))
            elif cmd in cli_config.despawn_commands:
                self.client.send_despawn()
            elif cmd in cli_config.ready_commands:
                self.client.send_ready()
            elif cmd in cli_config.not_ready_commands:
                self.client.send_not_ready()
            elif cmd in cli_config.quit_commands:
                self.client.state = ClientState.DISCONNECTED

    def play_game(self) -> None:
        """Sends player actions and displays game state"""
        while self.client.state is ClientState.PLAYING:
            cmd = input()

            if cmd in cli_config.up_commands:
                self.client.send_action(PlayerAction.MOVE_UP)
            elif cmd in cli_config.down_commands:
                self.client.send_action(PlayerAction.MOVE_DOWN)
            elif cmd in cli_config.left_commands:
                self.client.send_action(PlayerAction.MOVE_LEFT)
            elif cmd in cli_config.right_commands:
                self.client.send_action(PlayerAction.MOVE_RIGHT)
            elif cmd in cli_config.bomb_commands:
                self.client.send_action(PlayerAction.PLANT_BOMB)
            elif cmd in cli_config.quit_commands:
                self.client.state = ClientState.DISCONNECTED

    def display_environment(self, environment: Environment) -> None:
        """Displays the environment

        :param environment: The environment data
        """
        print("\n" * shutil.get_terminal_size().lines)  # Clear screen
        print(
            f"move up: {cli_config.up_commands[0]}",
            f"move down: {cli_config.down_commands[0]}",
            f"move left: {cli_config.left_commands[0]}",
            f"move right: {cli_config.right_commands[0]}",
            f"plant bomb: {cli_config.bomb_commands[0]}",
            f"quit game: {cli_config.quit_commands[0]}",
            sep="\n",
        )
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
    raise SystemExit(main())
