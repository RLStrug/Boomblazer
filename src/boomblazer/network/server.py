#!/usr/bin/env python3
"""Implements a game server"""

from __future__ import annotations

import argparse
import contextlib
import json
import pathlib
import logging
import sys
import typing

from ..config.game import game_config
from ..config.game_folders import game_folders_config
from ..environment.entity.player import Player
from ..environment.entity.player import PlayerAction
from ..environment.environment import Environment
from ..environment.map import Map
from ..environment.map import MapError
from ..metadata import GAME_NAME
from ..utils.argument_parser import base_parser
from ..utils.argument_parser import handle_base_arguments
from ..utils.repeater import Repeater
from .address import Address
from .network import Network

if typing.TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Sequence
    from collections.abc import Set
    from importlib.resources.abc import Traversable
    from types import TracebackType
    from typing import Any
    from typing import Self


class ServerError(Exception):
    """Exception thrown when an error occurs in the server"""


class Server(Network):
    """Implements server side of the network protocol

    Class Constants:
        _CLIENT_MESSAGE_WAIT_TIME: float
            Number of seconds during which the server waits for a client
            message before checking quickly if the game ended on abruptly.
            Ideally, this should not be 0.0 in order to avoid using 100% CPU
            for nothing. The value should not be too high either to avoid
            looking unresponsive to the user, even though the event should not
            happen often
    """

    __slots__ = {
        "environment": "(Environment) Game environment",
        "clients": "(dict[Address, Player]) Links connected players to their address",
        "is_running": "(bool) Defines if the server is running or over",
        "_player_actions": "(dict[Player, PlayerAction]) Players actions for next tick",
        "_tick_thread": "(Repeater) Thread used to update the game environment",
    }

    _CLIENT_MESSAGE_WAIT_TIME = 0.5

    def __init__(self, addr: Address, map_filename: str, **kwargs: Any) -> None:
        """Initialize the Server object

        :param addr: Interface and port on which the server will listen
        :param map_filename: File containing the map environment initial data
        """
        super().__init__(**kwargs)
        self.bind(addr)
        self.clients: dict[Address, Player] = {}

        map_filepath = self._find_map_file(map_filename)
        try:
            map_ = Map.from_file(map_filepath)
        except MapError as exc:
            raise ServerError(exc) from exc
        self.environment = Environment(map_)

        self.is_running = True
        self._player_actions: dict[Player, PlayerAction] = {}
        self._tick_thread = Repeater()

    def _find_map_file(self, map_filename: str) -> Traversable:
        """Searches for map file in all folders defined in config

        Looks for map file in official maps folder first, then in custom maps folder.
        If the file is not found, return path to filename in current working directory

        :param map_filename: Map filename
        :returns: Map filepath
        """
        for maps_folder in game_folders_config.maps_folders:
            map_filepath = maps_folder / map_filename
            if map_filepath.is_file():
                return map_filepath
            self._logger.debug("%r not in %r", map_filename, str(maps_folder))
        # If file not in defined folders, try current working directory
        return pathlib.Path(".", map_filename)

    # ---------------------------------------- #
    # GAME STATE
    # ---------------------------------------- #

    def start(self) -> None:
        """Start the server

        Waits for the players and initializes the game map environment
        """
        while self.is_running:
            self.wait_players()

            if not self.is_running:
                break

            self.launch_game()
            if self._tick_thread.ident is not None:
                self._tick_thread.stop()
                self._tick_thread.join()

    def wait_players(self) -> None:
        """Waits for players to connect until everyone is ready"""
        self._logger.info("Waiting for players")
        ready_players: set[Address] = set()
        # Wait until all players are ready to start
        while len(self.clients) < 1 or len(ready_players) != len(self.clients):
            # Do not wait indefinitely in case server closed abruptly
            events = self.selector.select(self._CLIENT_MESSAGE_WAIT_TIME)
            # If server is closed, no need to check for messages
            if not self.is_running:
                break
            # If no messages, go back to waiting
            if not events:
                continue

            msg, addr = self.recv_message()
            if msg is None:
                # Skip bad message
                continue
            command, arg = msg
            if command == b"JOIN":
                self.add_player(addr, arg)
            elif command == b"QUIT":
                if addr in ready_players:
                    ready_players.remove(addr)
                self.remove_player(addr)
            elif command == b"READY":
                if addr in ready_players:
                    ready_players.remove(addr)
                else:
                    ready_players.add(addr)
            else:  # Skip unknown command
                continue
            self.send_players_list(ready_players)

    def launch_game(self) -> None:
        """Runs the game logic from clients inputs

        Starts a thread that will update the game environment every tick
        Handles user input as they come on the main thread
        """
        self._logger.info("Game start")
        self.environment.spawn_players()
        self.send_environment()
        self._tick_thread = Repeater(
            target=self.tick, interval=game_config.tick_frequency, name="server-tick"
        )
        self._tick_thread.start()

        self.handle_players_inputs()
        # Should not stop game unless server is closing
        # self.send_stop_game(b"PLACEHOLDER wins")

    # ---------------------------------------- #
    # GAME
    # ---------------------------------------- #

    def tick(self) -> None:
        """Updates the game environment every tick and sends it to clients"""
        self.environment.tick(self._player_actions)
        self.send_environment()
        self.reset_player_actions()

    def reset_player_actions(self) -> None:
        """Resets players' commands after the end of the tick"""
        self._player_actions = {}

    def handle_players_inputs(self) -> None:
        """Handle each player's action for current tick"""
        # Handle players input until there is no living player
        while len(self.environment.players) > 0:
            # Do not wait indefinitely in case server closed abruptly
            events = self.selector.select(self._CLIENT_MESSAGE_WAIT_TIME)
            # If server is closed, no need to check for messages
            if not self.is_running:
                break
            # If no messages, go back to waiting
            if not events:
                continue

            msg, addr = self.recv_message()
            if msg is None or addr not in self.clients:
                continue

            player = self.clients[addr]
            cmd, arg = msg
            if cmd == b"MOVE":
                if arg == b"UP":
                    self._player_actions[player] = PlayerAction.MOVE_UP
                elif arg == b"DOWN":
                    self._player_actions[player] = PlayerAction.MOVE_DOWN
                elif arg == b"LEFT":
                    self._player_actions[player] = PlayerAction.MOVE_LEFT
                elif arg == b"RIGHT":
                    self._player_actions[player] = PlayerAction.MOVE_RIGHT
            elif cmd == b"BOMB":
                self._player_actions[player] = PlayerAction.PLANT_BOMB
            elif cmd == b"QUIT":
                self.remove_player(addr)

    # ---------------------------------------- #
    # PLAYERS / CLIENTS HANDLING
    # ---------------------------------------- #

    def add_player(self, addr: Address, name: bytes) -> None:
        """Adds a player to the clients list

        :param addr: New client address
        :param name: New player's name
        """
        player = self.environment.add_player(name.decode("utf8"))
        if player is not None:
            self.clients[addr] = player

    def remove_player(self, addr: Address) -> None:
        """Removes a player from the clients list

        Will fail silently if the address is not associated to a player.

        :param addr: Client's address
        """
        with contextlib.suppress(ValueError, KeyError):
            player = self.clients[addr]
            self.environment.remove_player(player)
            del self.clients[addr]

    # ---------------------------------------- #
    # NETWORK COMMUNICATIONS
    # ---------------------------------------- #

    # @override
    def send_message(
        self, command: bytes, arg: bytes, peers: Iterable[Address] | None = None
    ) -> None:
        """Sends a message to all clients

        :param command: Command to send to the client
        :param arg: Argument associated to `command`
        :param peers: Peers at whom the message will be sent (default: all clients)
        """
        if peers is None:
            peers = self.clients.keys()
        super().send_message(command, arg, peers)

    # ---------------------------------------- #
    # SEND SERVER COMMANDS
    # ---------------------------------------- #

    def send_players_list(self, ready_players: Set[Address]) -> None:
        """Sends the list of connected players' name

        :param ready_players: Players that are ready to start the game
        """
        players_list = json.dumps(
            {
                player.name: (addr in ready_players)
                for addr, player in self.clients.items()
            }
        ).encode("utf8")
        self.send_message(b"PLAYERS_LIST", players_list)

    def send_stop_game(self, reason: bytes) -> None:
        """Tells all clients that the server is closed and why

        :param reason: Reason why the server is closing
        """
        self.send_message(b"STOP", reason)

    def send_environment(self) -> None:
        """Sends the current game environment state"""
        self.send_message(
            b"ENVIRONMENT",
            self.environment.to_json(separators=(",", ":")).encode("utf8"),
        )

    # ---------------------------------------- #
    # CONTEXT MANAGER
    # ---------------------------------------- #

    # @override
    def close(self) -> None:
        """Closes the server"""
        self.is_running = False
        if self._tick_thread.ident is not None:
            self._tick_thread.stop()
            self._tick_thread.join()

        self.send_stop_game(b"Server closing")
        super().close()

    def __enter__(self) -> Self:
        """Enters a context manager (with statement)

        :returns: The instance itself
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exits a context manager (with statement)

        :param exc_type: Type of the exception that occured during the context
        :param exc_val: Value of the exception that occured during the context
        :param exc_tb: Traceback of the exception that occured during the context
        :returns: None (exceptions are propagated)
        """
        self.close()


def main(argv: Sequence[str] | None = None) -> int:
    """Instanciates a Server

    :param argv: If None, uses command line arguments
    """
    parser = argparse.ArgumentParser(parents=[base_parser])
    parser.add_argument(
        "--address", metavar="[[HOST]:[PORT]]", type=Address.from_string, default=""
    )
    parser.add_argument("map_filename", type=pathlib.Path)
    args = parser.parse_args(argv)

    handle_base_arguments(args)
    logger = logging.getLogger(f"{GAME_NAME}.server")
    with Server(args.address, args.map_filename, logger=logger) as server:
        server.start()

    return 0


if __name__ == "__main__":
    sys.exit(main())
