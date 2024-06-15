"""Base UI model

Enumerations:
    GameState: Enum
        Defines in what states the game currently is

Classes:
    BaseUI:
        The base class for client UIs

Constants:
    _ALL_INTERFACES: str
        The IP address representing all interfaces available
    _LOCAL_HOST: str
        The IP address of the local machine
"""

import enum
import logging
import pathlib
import threading
from abc import ABC
from types import TracebackType
from typing import Optional
from typing import Type

from boomblazer.config.game_folders import game_folders_config
from boomblazer.network.client import Client
from boomblazer.network.address import Address
from boomblazer.network.server import Server


_ALL_INTERFACES = "0.0.0.0"
_LOCAL_HOST = "127.0.0.1"

class GameState(enum.Enum):
    """Defines in what states the game currently is
    """
    MAIN_MENU = enum.auto()
    LOBBY = enum.auto()
    PLAYING = enum.auto()
    DEAD = enum.auto()
    SPECTATE = enum.auto()
    GAME_OVER = enum.auto()


class BaseUI(ABC):
    """The base class for client UIs

    Members:
        _logger: logging.Logger
            Logs the messages of the UI
        client: Client
            The client associated with this UI
        server: Server
            The server associated with this UI
        _server_thread: threading.Thread
            Thread used to launch local server

    Special methods:
        __init__:
            Initializes a new BaseUI
        __enter__:
            Enters a context manager (with statement)
        __exit__:
            Exits a context manager (with statement)

    Methods:
        join_game:
            Joins a game
        create_game:
            Creates a game
        create_game_and_join:
            Creates a game and joins it
        close:
            Closes the client and the local server
    """

    __slots__ = (
        "_logger", "client", "server", "_server_thread",
    )

    def __init__(
            self, *,
            logger: logging.Logger
    ) -> None:
        """Initializes a new BaseUI

        Named only parameters:
            logger: logging.Logger
                The game message logger
        """
        self._logger = logger
        self.client = None
        self.server = None
        self._server_thread = threading.Thread()

    def join_game(
            self, addr: Address, username: str
    ) -> None:
        """Joins a game

        Parameters:
            addr: Address
                The address of the server
            username: str
                The player's name
        """
        self.client = Client(
            addr, username.encode("utf8"), logger=self._logger
        )
        self.client.start()

    def create_game(
            self, addr: Address, map_filename: str
    ) -> None:
        """Creates a game

        Parameters:
            addr: Address
                The interface and port of the server
            map_filename: str
                The file containing the initial map environment data
        """
        self.server = Server(addr, map_filename, logger=self._logger)
        # Unlike Client.start, which returns after connection, Server.start
        # returns after game is over. So we need to execute it in a different
        # thread
        self._server_thread = threading.Thread(
            target=self.server.start, name="server"
        )
        self._server_thread.start()

    def create_game_and_join(
            self, address: Address, username: str, map_filename: str
    ) -> None:
        """Creates a game and joins it

        Parameters:
            address: Address
                The interface and port on which the server will listen
            username:
                The player's name
            map_filename: str
                The file containing the initial map environment data
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
        """Closes the client and the local server
        """
        if self.server is not None:
            if self._server_thread.ident is not None:
                self.server.is_game_running = False
                self._server_thread.join()
            self.server.close()
        if self.client is not None:
            self.client.close()

    def __enter__(self) -> "BaseUI":
        """Enters a context manager (with statement)

        Return value: BaseUI
            The instance itself
        """
        return self

    def __exit__(
            self, exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType]
    ) -> None:
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

        Return value: None
            Does not return a value. This means that if an exception occurred,
            it should be propagated, not ignored
        """
        self.close()
