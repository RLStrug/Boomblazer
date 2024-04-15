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

from boomblazer.network.client import Client
from boomblazer.network.network import AddressType
from boomblazer.network.server import Server
from boomblazer.utils import create_logger


_ALL_INTERFACES = "0.0.0.0"
_LOCAL_ADDRESS = "127.0.0.1"

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
        self.server = None
        self._server_thread = None

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
        self.client.start()

    def create_game(self, addr: AddressType, map_filename: Path) -> None:
        """Creates a game

        Parameters:
            addr: AddressType
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
            self, port: int, username: str, map_filename: Path
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
        addr_for_server = (_ALL_INTERFACES, port)
        self.create_game(addr_for_server, map_filename)

        addr_for_client = (_LOCAL_ADDRESS, port)
        self.join_game(addr_for_client, username, True)

    # ---------------------------------------- #
    # CONTEXT MANAGER
    # ---------------------------------------- #

    def close(self) -> None:
        """Closes the client and the local server
        """
        if self.server is not None:
            if self._server_thread is not None:
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
