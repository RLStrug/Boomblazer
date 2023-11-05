"""Base UI model

Enumerations:
    GameState: Enum
        Defines in what states the game currently is

Classes:
    BaseUI:
        The base class for client UIs

Constants:
    _LOCAL_ADDRESS: str
        The IP address of the local machine
"""

import enum
import threading
from abc import ABC
from pathlib import Path
from types import TracebackType
from typing import Optional
from typing import Type

from client import Client
from network import AddressType
from server import Server
from utils import create_logger


_LOCAL_ADDRESS = "127.0.0.1"

class GameState(enum.Enum):
    """Defines in what states the game currently is"""
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
            Closes the client
    """

    __slots__ = (
        "_logger", "client",
    )

    def __init__(
            self, *,
            verbosity: int = 0, log_file: Optional[Path] = None
    ) -> None:
        """Initializes a new BaseUI

        Named only parameters:
            verbosity: int
                Defines how verbose the logger should be
            log_file: Optional[Path]
                Defines which file the logger should record its messages to.
                Defaults to stderr if not specified
        """
        self._logger = create_logger(__name__, verbosity, log_file)
        self.client = None

    def join_game(
            self, addr: AddressType, username: str, is_host: bool = False
    ) -> None:
        """Joins a game

        Parameters:
            addr: AddressType
                The address of the server
            username: str
                The player's name
            is_host: bool
                Specifies if this is the host client
        """
        self.client = Client(
            addr, username.encode("utf8"), is_host, logger=self._logger
        )
        self.client.send_join()

    def create_game(self, *args, **kwargs) -> None:
        """Creates a game
        """
        raise NotImplementedError("Cannot create server from UI yet")

    def create_game_and_join(
            self, port: int, username: str, map_filename: str
    ) -> None:
        """Creates a game and joins it

        Parameters:
            port: int
                The port number on which the server will listen
            username:
                The player's name
            map_filename: str
                The file containing the initial map environment data
        """
        addr = (_LOCAL_ADDRESS, port)
        self.create_game(addr, map_filename)
        self.join_game(addr, username, True)

    # ---------------------------------------- #
    # CONTEXT MANAGER
    # ---------------------------------------- #

    def close(self) -> None:
        """Closes the client
        """
        if self.client is not None:
            self.client.close()
            self.client = None

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
    ) -> bool:
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

        Return value: bool
            Always returns `False`. This means that if an exception occurred,
            it should be propagated, not ignored
        """
        self.close()
