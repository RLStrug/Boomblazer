#!/usr/bin/env python3
"""Implements a game server

Classes:
    Server:
        Implements server side of the network protocol

Exception classes:
    ServerError: Exception
        Exception thrown when an error occurs in the server
"""

import argparse
import json
import selectors
import sys
import threading
import time
from pathlib import Path
from types import TracebackType
from typing import Iterable
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Type

from boomblazer.argument_parser import base_parser
from boomblazer.argument_parser import handle_base_arguments
from boomblazer.config.server import server_config
from boomblazer.game_handler import GameHandler
from boomblazer.game_handler import MoveActionEnum
from boomblazer.map_environment import MapEnvironment
from boomblazer.network.network import AddressType
from boomblazer.network.network import Network
from boomblazer.entity.player import Player


class ServerError(Exception):
    """Exception thrown when an error occurs in the server
    """


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

    Members:
        game_handler: GameHandler
            Contains the game state and logic
        clients: dict[AddressType, Player]
            Links connected players to their address
        _map_filename: Path
            Path to map that will be used for the game
        _logger: logging.Logger
            The server logger
        is_game_running: bool
            Defines if the game is running or over
        _player_actions: Dict[Player, Tuple[bool, MoveActionEnum]]:
            Actions to be performed by players during next game tick
        _tick_thread: threading.Thread
            Thread used to update the game environment at regular interval

    Special method:
        __init__:
            Initialize the Server object
        __enter__:
            Allows using the context manager (with statement)
        __exit__:
            Allows using the context manager (with statement)

    Methods:
        start:
            Start the game
        wait_players:
            Waits for players to connect until everyone is ready
        launch_game:
            Runs the game logic from clients inputs
        tick:
            Updates the game environment every tick and sends it to clients
        reset_player_actions:
            Resets players' commands after the end of the tick
        handle_players_inputs:
            Handle each player's action for current tick
        add_player:
            Adds a player to the clients list, and send the list to players
        remove_player:
            Removes a player from the clients list
        recv_message:
            Recieves a message from network
        send_message:
            Sends a message to all clients
        send_players_list:
            Sends the list of connected players' name
        send_stop_game:
            Tells all clients that the server is closed and why
        send_map:
            Sends the current map state
        close:
            Closes the server
    """

    __slots__ = (
        "game_handler", "clients", "_map_filename",
        "is_game_running", "_player_actions", "_tick_thread",
    )

    _CLIENT_MESSAGE_WAIT_TIME = 0.5

    def __init__(
            self, addr: AddressType, map_filename: Path, *args, **kwargs
    ) -> None:
        """Initialize the Server object

        Parameters:
            addr: AddressType
                The IP and the port on which the server will run
            map_filename: Path
                File containing the map environment initial data
        """
        super().__init__(*args, **kwargs)
        self.bind(addr)
        self.clients = {}
        self.game_handler = None
        self._map_filename = map_filename
        self.is_game_running = False
        self._player_actions = {}
        self._tick_thread = None

        if not self._map_filename.is_file():
            raise ServerError("Given map file is not a file")

    # ---------------------------------------- #
    # GAME STATE
    # ---------------------------------------- #

    def start(self) -> None:
        """Start the game

        Waits for the players and initializes the game map environment
        """
        self.wait_players()
        map_environment = MapEnvironment.from_file(
            self._map_filename, list(self.clients.values())
        )
        self.game_handler = GameHandler(map_environment)
        self.launch_game()

    def wait_players(self) -> None:
        """Waits for players to connect until everyone is ready
        """
        self._logger.info("Waiting for players")
        ready_players: Set[AddressType] = set()
        while (
                len(self.clients) < 1 or
                len(ready_players) != len(self.clients)
        ):
            # TODO Do not wait indefinitely
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
        self.is_game_running = True
        self.send_map()
        self._tick_thread = threading.Thread(
            target=self.tick, name="server-tick"
        )
        self._tick_thread.start()

        self.handle_players_inputs()
        # Should not stop game unless server is closing
        # self.send_stop_game(b"PLACEHOLDER wins")

    # ---------------------------------------- #
    # GAME
    # ---------------------------------------- #

    def tick(self):
        """Updates the game environment every tick and sends it to clients
        """
        while self.is_game_running:
            start_time = time.monotonic()

            actions = [
                (player, *action)
                for player, action in self._player_actions.items()
            ]

            self.game_handler.tick(actions)
            self.send_map()
            self.reset_player_actions()

            end_time = time.monotonic()
            time_spent = end_time - start_time
            if time_spent < server_config.tick_frequency:
                time.sleep(server_config.tick_frequency - time_spent)

    def reset_player_actions(self):
        """Resets players' commands after the end of the tick
        """
        self._player_actions = {}

    def handle_players_inputs(self):
        """Handle each player's action for current tick
        """
        sel = selectors.DefaultSelector()
        sel.register(self.sock, selectors.EVENT_READ)

        while self.is_game_running:
            # Do not wait indefinitely in case game ended abruptly
            events = sel.select(self._CLIENT_MESSAGE_WAIT_TIME)
            if not events:
                continue

            msg, addr = self.recv_message()
            if msg is None or addr not in self.clients:
                continue

            player = self.clients[addr]
            cmd, arg = msg
            if cmd == b"MOVE":
                if arg == b"UP":
                    self._player_actions[player] = (False, MoveActionEnum.MOVE_UP)
                elif arg == b"DOWN":
                    self._player_actions[player] = (False, MoveActionEnum.MOVE_DOWN)
                elif arg == b"LEFT":
                    self._player_actions[player] = (False, MoveActionEnum.MOVE_LEFT)
                elif arg == b"RIGHT":
                    self._player_actions[player] = (False, MoveActionEnum.MOVE_RIGHT)
            elif cmd == b"BOMB":
                self._player_actions[player] = (True, MoveActionEnum.DONT_MOVE)
            elif cmd == b"QUIT":
                self.remove_player(addr)


    # ---------------------------------------- #
    # PLAYERS / CLIENTS HANDLING
    # ---------------------------------------- #

    def add_player(self, addr: AddressType, name: bytes) -> None:
        """Adds a player to the clients list

        Parameters:
            addr: AddressType
                The new clients IP and port
            name: bytes
                The new player's name
        """
        self.clients[addr] = Player(name.decode("utf8"))

    def remove_player(self, addr: AddressType) -> None:
        """Removes a player from the clients list

        Parameters:
            addr:
                The player's IP and port
        """
        if addr in self.clients:
            # If players are not in the game yet (lobby)
            if self.game_handler is not None:
                player = self.clients[addr]
                # If player not dead yet
                if player in self.game_handler.map_environment.players:
                    self.game_handler.map_environment.players.remove(player)
            del self.clients[addr]
        if len(self.clients) == 0 and self.is_game_running:
            self.close()

    # ---------------------------------------- #
    # NETWORK COMMUNICATIONS
    # ---------------------------------------- #

    # @override
    def send_message(
            self, command: bytes, arg: bytes,
            peers: Optional[Iterable[AddressType]] = None
    ) -> None:
        """Sends a message to all clients

        Parameters:
            command: bytes
                The command to send to the server
            arg: bytes
                The argument associated to `command`
            peers: Optional[Iterable[AddressType]] (default = None)
                The peers at whom the message will be sent
                If None, the message will be sent to all clients
        """
        if peers is None:
            peers = self.clients.keys()
        super().send_message(command, arg, peers)

    # ---------------------------------------- #
    # SEND SERVER COMMANDS
    # ---------------------------------------- #

    def send_players_list(
            self, ready_players: Set[AddressType] = frozenset
    ) -> None:
        """Sends the list of connected players' name

        Parameters:
            ready_players: set[AddressType]
                Players that are ready to start the game
        """
        players_list = json.dumps({
            player.name: (addr in ready_players)
            for addr, player in self.clients.items()
        }).encode("utf8")
        self.send_message(b"PLAYERS_LIST", players_list)

    def send_stop_game(self, reason: bytes) -> None:
        """Tells all clients that the server is closed and why

        Parameters:
            reason: bytes
                The reason why the server closes
        """
        self.send_message(b"STOP", reason)

    def send_map(self) -> None:
        """Sends the current map state
        """
        map_environment = self.game_handler.map_environment
        self.send_message(
            b"MAP",
            map_environment.to_json(separators=(',',':')).encode("utf8")
        )

    # ---------------------------------------- #
    # CONTEXT MANAGER
    # ---------------------------------------- #

    # @override
    def close(self) -> None:
        """Closes the server
        """
        self.is_game_running = False
        if self._tick_thread is not None:
            self._tick_thread.join()

        self.send_stop_game(b"Server closing")
        super().close()

    def __enter__(self) -> "Server":
        """Enters a context manager (with statement)

        Return value: Server
            The instance itself
        """
        return self

    def __exit__(
            self, exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType]
    ) -> Optional[bool]:
        """Exits a context manager (with statement)

        Parameters:
            exc_type: Optional[type[BaseException]]
                The type of the exception that occured during the context
                management, or `None` if none occured
            exc_val: Optional[BaseException]
                The value of the exception that occured during the context
                management, or `None` if none occured
            exc_tb: Optional[TracebackType]
                The traceback of the exception that occured during the context
                management, or `None` if none occured

        Return value: Optional[bool]
            Always returns `False` or `None`. This means that if an exception
            occurred, it should be propagated, not ignored
        """
        self.close()


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Instanciates a Server

    Parameters:
        argv: Sequence[str] | None
            If None, uses command line arguments
    """
    parser = argparse.ArgumentParser(parents=[base_parser])
    parser.add_argument("address", nargs="?", default="0.0.0.0")
    parser.add_argument("port", type=int)
    parser.add_argument("map_filename", type=Path)
    args = parser.parse_args(argv)

    addr = (args.address, args.port)
    base_args = handle_base_arguments(args)
    with Server(addr, args.map_filename, logger=base_args.logger) as server:
        server.start()

    return 0


if __name__ == "__main__":
    sys.exit(main())
