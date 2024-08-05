"""Implements a game client"""

from __future__ import annotations

import json
import threading
import typing

from ..config.client import client_config
from ..environment.entity.player import PlayerAction
from ..environment.environment import Environment
from .address import Address
from .address import UNDEFINED_ADDRESS
from .network import Network

if typing.TYPE_CHECKING:
    from collections.abc import Iterable
    from types import TracebackType
    from typing import Any
    from typing import Self


class ClientError(Exception):
    """Exception thrown when an error occurs in the client"""


class Client(Network):
    """Implements client side of the network protocol

    This class handles all the communication from the player to the server
    hosting the game. It translates the player's actions performed through the
    UI into packets readable by the server, and updates the game state from the
    packets recieved from the server

    Class Constants:
        _SERVER_MESSAGE_WAIT_TIME: float
            Number of seconds during which the client waits for a server update
            before checking quickly if the game ended on abruptly. Ideally,
            this should not be 0.0 in order to avoid using 100% CPU for
            nothing. The value should not be too high either to avoid looking
            unresponsive to the user, even though the event should not happen
            often
    """

    __slots__ = {
        "server_addr": "(Address) Address of the remote game server",
        "username": "(str) Name of the player",
        "environment": "(Environment) Defines the current game environment",
        "is_game_running": "(bool) Defines if the game is running or over",
        "_tick_thread": "(threading.Thread) Thread that updates the game environment",
        "update_semaphore": "(threading.semaphore) Marks if server sent an update",
        "connected_players": "(dict[str, bool]) Players readyness state",
    }

    _SERVER_MESSAGE_WAIT_TIME = 0.5

    def __init__(
        self,
        server_addr: Address = UNDEFINED_ADDRESS,
        username: bytes = b"",
        **kwargs: Any,
    ) -> None:
        """Initializes a new Client

        :param server_addr: Address of the server hosting the game
        :param username: Name of the player
        """
        super().__init__(**kwargs)
        self.server_addr = server_addr
        self.username = username
        self.environment = Environment()
        self.is_game_running = False
        self._tick_thread = threading.Thread()
        self.update_semaphore = threading.Semaphore()
        self.connected_players: dict[str, bool] = {}

    # ---------------------------------------- #
    # GAME
    # ---------------------------------------- #

    def start(self) -> None:
        """Joins the server and sets up the reception af server packets"""
        if self.server_addr is UNDEFINED_ADDRESS:
            raise ClientError("Server address undefined")

        for _ in range(client_config.max_connect_tries):
            self.send_join()
            events = self.selector.select(client_config.max_connect_wait)
            if not events:
                continue

            self.is_game_running = True
            self.update_semaphore = threading.Semaphore()
            self._logger.info(
                "Connected to %s:%d", self.server_addr[0], self.server_addr[1]
            )
            self._tick_thread = threading.Thread(target=self.tick, name="client-tick")
            self._tick_thread.start()
            return

        # If connection failed
        self._logger.info(
            "Failed to connect to %s:%d", self.server_addr[0], self.server_addr[1]
        )

    def tick(self) -> None:
        """Updates the game environment every time the server sends a message"""
        while self.is_game_running:
            # Do not wait indefinitely in case game ended abruptly
            events = self.selector.select(self._SERVER_MESSAGE_WAIT_TIME)
            if not events:
                continue

            msg, addr = self.recv_message()
            if msg is None or addr != self.server_addr:
                continue

            cmd, arg = msg
            if cmd == b"PLAYERS_LIST":
                self.connected_players = json.loads(arg)
            elif cmd == b"ENVIRONMENT":
                self.environment = Environment.from_json(arg)
            elif cmd == b"STOP":
                self.is_game_running = False
                break
            else:
                continue

            # Try to consume the token first in case updating local state is
            # somehow slower than recieving updates from network
            self.update_semaphore.acquire(blocking=False)
            self.update_semaphore.release()

    # ---------------------------------------- #
    # NETWORK COMMUNICATIONS
    # ---------------------------------------- #

    # @override
    def send_message(
        self,
        command: bytes,
        arg: bytes = b"",
        peers: Iterable[Address] | None = None,
    ) -> None:
        """Sends a message to the server hosting the game

        :param command: Command to send to the server
        :param arg: Argument associated to `command`
        """
        if peers is None:
            peers = (self.server_addr,)
        super().send_message(command, arg, peers)

    # ---------------------------------------- #
    # SEND CLIENT COMMANDS
    # ---------------------------------------- #

    def send_ready(self) -> None:
        """Tells the server we are ready to start the game

        If the command is sent multiple times, it will alternate the client
        status from ready to not ready.
        This command should have an effect on the server only if the game has
        not yet been started.
        """
        self.send_message(b"READY")

    def send_join(self) -> None:
        """Tells the server to let the player join the game

        This command should have an effect on the server only if the game has
        not yet been started.
        """
        command = b"JOIN"
        self.send_message(command, self.username)

    def send_move(self, action: PlayerAction) -> None:
        """Tells the server that the player wants to move

        This command should have an effect on the server only if the game has
        already been started.
        """
        if action == PlayerAction.MOVE_UP:
            self.send_message(b"MOVE", b"UP")
        elif action == PlayerAction.MOVE_DOWN:
            self.send_message(b"MOVE", b"DOWN")
        elif action == PlayerAction.MOVE_LEFT:
            self.send_message(b"MOVE", b"LEFT")
        elif action == PlayerAction.MOVE_RIGHT:
            self.send_message(b"MOVE", b"RIGHT")

    def send_plant_bomb(self) -> None:
        """Tells the server that the player wants to plant a bomb

        This command should have an effect on the server only if the game has
        already been started.
        """
        self.send_message(b"BOMB")

    def send_quit(self) -> None:
        """Tells the server that the player wants to quit the game"""
        self.send_message(b"QUIT")

    # ---------------------------------------- #
    # CONTEXT MANAGER
    # ---------------------------------------- #

    # @override
    def close(self) -> None:
        """Closes the network connections"""
        self.is_game_running = False
        if self._tick_thread.ident is not None:
            self._tick_thread.join()
        if self.server_addr is not UNDEFINED_ADDRESS:
            self.send_quit()
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

        :param exc_type: The type of the exception that occured during the context
        :param exc_val: The value of the exception that occured during the context
        :param exc_tb: The traceback of the exception that occured during the context
        :returns: None (exceptions are propagated)
        """
        self.close()
