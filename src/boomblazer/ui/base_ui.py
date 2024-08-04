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
    }

    def __init__(self, *, logger: logging.Logger) -> None:
        """Initializes a new BaseUI

        Named only parameters:
            logger: logging.Logger
                Game message logger
        """
        self._logger = logger
        self.client = Client(logger=logger)
        self.server: Server | None = None
        self._server_thread = threading.Thread()

    def join_game(self, addr: Address, username: str) -> None:
        """Joins a game

        Parameters:
            addr: Address
                Address of the server
            username: str
                Player's name
        """
        self.client.server_addr = addr
        self.client.username = username.encode("utf8")
        self.client.start()

    def create_game(self, addr: Address, map_filename: str) -> None:
        """Creates a game

        Parameters:
            addr: Address
                Interface and port of the server
            map_filename: str
                File containing the initial map environment data
        """
        self.server = Server(addr, map_filename, logger=self._logger)
        # Unlike Client.start, which returns after connection, Server.start
        # returns after game is over. So we need to execute it in a different
        # thread
        self._server_thread = threading.Thread(target=self.server.start, name="server")
        self._server_thread.start()

    def create_game_and_join(
        self, address: Address, username: str, map_filename: str
    ) -> None:
        """Creates a game and joins it

        Parameters:
            address: Address
                Interface and port on which the server will listen
            username:
                Player's name
            map_filename: str
                File containing the initial map environment data
        """
        self.create_game(address, map_filename)

        if address.host in ("", _ALL_INTERFACES):
            address_for_client = Address(_LOCAL_HOST, address.port)
        else:
            address_for_client = address
        self.join_game(address_for_client, username)

    # ---------------------------------------- #
    # CONTEXT MANAGER
    # ---------------------------------------- #

    def close(self) -> None:
        """Closes the client and the local server"""
        if self.server is not None:
            self.server.close()
            if self._server_thread.ident is not None:
                self._server_thread.join()
        self.client.close()

    def __enter__(self) -> Self:
        """Enters a context manager (with statement)

        Return value: BaseUI
            The instance itself
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exits a context manager (with statement)

        Parameters:
            exc_type: type[BaseException] | None
                Type of the exception that occured during the context
                management, or `None` if none occured
            exc_val: BaseException | None
                Value of the exception that occured during the context
                management, or `None` if none occured
            exc_tb: TracebackType | None
                Traceback of the exception that occured during the context
                management, or `None` if none occured

        Return value: None
            Does not return a value. This means that if an exception occurred,
            it should be propagated, not ignored
        """
        self.close()
