"""Base UI model

Constants:
    _ALL_INTERFACES: str
        IP address representing all interfaces available
    _LOCAL_HOST: str
        IP address of the local machine
"""

from __future__ import annotations

import abc
import enum
import logging
import threading
import typing

from ..network.address import Address
from ..network.client import Client
from ..network.server import Server

if typing.TYPE_CHECKING:
    from types import TracebackType
    from typing import Self
    from ..environment.environment import Environment


_ALL_INTERFACES = "0.0.0.0"
_LOCAL_HOST = "127.0.0.1"


class GameState(enum.Enum):
    """Defines in what states the game currently is"""

    MAIN_MENU = enum.auto()
    LOBBY = enum.auto()
    PLAYING = enum.auto()
    DEAD = enum.auto()
    SPECTATE = enum.auto()
    GAME_OVER = enum.auto()


class BaseUI(abc.ABC):
    """The base class for client UIs"""

    __slots__ = {
        "_logger": "(logging.Logger) Logs the messages of the UI",
        "client": "(Client) Client associated with this UI",
        "server": "(Server) Server associated with this UI",
        "_server_thread": "(threading.Thread) Thread used to launch local server",
        "_client_thread": "(threading.Thread) Thread used to launch local client",
    }

    def __init__(self, *, logger: logging.Logger) -> None:
        """Initializes a new BaseUI

        Named only parameters:
            logger: logging.Logger
                Game message logger
        """
        self._logger = logger
        self.client = Client(self.display_environment, logger)
        self.server = Server(logger)
        self._client_thread = threading.Thread()
        self._server_thread = threading.Thread()

    def join_game(self, address: Address, username: str) -> None:
        """Joins a game

        :param address: Address of the server
        :param username: Player's name
        """
        self.client.connect(address, username.encode("utf8"))
        self._client_thread = threading.Thread(target=self.client.start, name="client")
        self._client_thread.start()

    def create_game(self, address: Address, map_filename: str) -> None:
        """Creates a game

        :param address: Interface and port of the server
        :param map_filename: File containing the initial map environment data
        """
        self.server.bind(address)
        self.server.load_map_from_file(map_filename)
        self._server_thread = threading.Thread(target=self.server.start, name="server")
        self._server_thread.start()

    def create_game_and_join(
        self, address: Address, username: str, map_filename: str
    ) -> None:
        """Creates a game and joins it

        :param address: Interface and port on which the server will listen
        :param username: Player's name
        :param map_filename: File containing the initial map environment data
        """
        self.create_game(address, map_filename)

        if address.host in ("", _ALL_INTERFACES):
            address_for_client = Address(_LOCAL_HOST, address.port)
        else:
            address_for_client = address
        self.join_game(address_for_client, username)

    @abc.abstractmethod
    def display_environment(self, environment: Environment) -> None:
        """Displays the environment

        :param environment: The environment data
        """

    # ---------------------------------------- #
    # CONTEXT MANAGER
    # ---------------------------------------- #

    def close(self) -> None:
        """Closes the client and the local server"""
        self.client.stop()
        if self._client_thread.ident is not None:
            self._client_thread.join()
        self.client.close()

        self.server.stop()
        if self._server_thread.ident is not None:
            self._server_thread.join()
        self.server.close()

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
