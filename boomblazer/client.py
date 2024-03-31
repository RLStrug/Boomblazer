"""Implements a game client

Classes:
    Client:
        The implementation of a client
"""

import logging
from pathlib import Path
from types import TracebackType
from typing import Iterable
from typing import Optional
from typing import Tuple
from typing import Type

from boomblazer.game_handler import GameHandler
from boomblazer.game_handler import MoveActionEnum
from boomblazer.network import AddressType
from boomblazer.network import MessageType
from boomblazer.network import Network
from boomblazer.utils import create_logger


class Client:
    """The implementation of a client that sends and recieves to/from a server

    This class handles all the communication from the player to the server
    hosting the game. It translates the player's actions performed through the
    UI into packets readable by the server, and updates the game state from the
    packets recieved from the server

    Members:
        _logger: logging.Logger
            The logger used to record the Client activity
        server_addr: AddressType
            The address of the remote game server
        is_host: bool
            Defines if this client is the host of the game
        network: Network
            Sends and recieves formatted messages to and from a server
        username: str
            Defines the name of the player
        game_handler: GameHandler
            Defines the current game state

    Special methods:
        __init__:
            Initializes a new Client
        __enter__:
            Enters a context manager (with statement)
        __exit__:
            Exits a context manager (with statement)

    Methods:
        recv_message:
            Recieves a message from the server hosting the game
        send_message:
            Sends a message to the server hosting the game
        send_start:
            Tells the server to start the game (host only)
        send_join:
            Tells the server to let the player join the game
        send_move:
            Tells the server that the player wants to move
        send_plant_bomb:
            Tells the server that the player wants to plant a bomb
        send_quit:
            Tells the server that the player wants to quit the game
        close:
            Closes the network connections
    """

    __slots__ = (
        "_logger", "server_addr", "is_host", "network", "username",
        "game_handler",
    )

    def __init__(self, server_addr: AddressType, username: bytes,
            is_host: bool = False, *,
            verbosity: int = 0, log_files: Optional[Iterable[Path]] = None,
            logger: Optional[logging.Logger] = None) -> None:
        """Initializes a new Client

        Parameters:
            server_addr: AddressType
                The IP address and port number of the server hosting the game
            username: str
                The name of the player
            is_host: bool
                Defines if this Client the game host

        Named only parameters:
            verbosity: int
                Defines how verbose the logger should be
            log_file: Optional[Path]
                Defines which file the logger should record its messages to.
                Defaults to stderr if not specified
            logger: Optional[logging.Logger]
                Defines the logger to be used by the Client instance.
                If this argument is given, `verbosity` and `log_files` will be
                ignored
        """

        self.server_addr = server_addr
        if logger is None:
            self._logger = create_logger(verbosity, log_files)
        else:
            self._logger = logger
        self.network = Network(self._logger)
        self.username = username
        self.is_host = is_host
        self.game_handler = None

    # ---------------------------------------- #
    # NETWORK WRAPPER
    # ---------------------------------------- #

    def recv_message(self) -> Tuple[Optional[MessageType], AddressType]:
        """Recieves a message from the server hosting the game

        Return value: tuple[Optional[MessageType], AddressType]
            A message sent by the server and the IP address and port number
            from which the message was recieved.
            The message contains a command and an argument, or is `None` if the
            message was invalid
        """
        return self.network.recv_message()

    def send_message(self, command: bytes, arg: bytes) -> None:
        """Sends a message to the server hosting the game

        Parameters:
            command: bytes
                The command to send to the server
            arg: bytes
                The argument associated to `command`
        """
        self.network.send_message(command, arg, (self.server_addr,))

    # ---------------------------------------- #
    # SEND CLIENT COMMANDS
    # ---------------------------------------- #

    def send_start(self) -> None:
        """Tells the server to start the game

        This command should have an effect on the server only if this instance
        is the host client.
        This command should have an effect on the server only if the game has
        not yet been started.
        """
        self.send_message(b"START", self.username)

    def send_join(self) -> None:
        """Tells the server to let the player join the game

        The command sent to the server will be different whether this instance
        is the host client or not.
        This command should have an effect on the server only if the game has
        not yet been started.
        """
        if self.is_host:
            command = b"HOST"
        else:
            command = b"JOIN"
        self.send_message(command, self.username)

    def send_move(self, action: MoveActionEnum) -> None:
        """Tells the server that the player wants to move

        This command should have an effect on the server only if the game has
        already been started.
        """
        if action == MoveActionEnum.MOVE_UP:
            self.send_message(b"MOVE", b"UP")
        elif action == MoveActionEnum.MOVE_DOWN:
            self.send_message(b"MOVE", b"DOWN")
        elif action == MoveActionEnum.MOVE_LEFT:
            self.send_message(b"MOVE", b"LEFT")
        elif action == MoveActionEnum.MOVE_RIGHT:
            self.send_message(b"MOVE", b"RIGHT")

    def send_plant_bomb(self) -> None:
        """Tells the server that the player wants to plant a bomb

        This command should have an effect on the server only if the game has
        already been started.
        """
        self.send_message(b"BOMB", b"")

    def send_quit(self) -> None:
        """Tells the server that the player wants to quit the game
        """
        self.send_message(b"QUIT", self.username)

    # ---------------------------------------- #
    # CONTEXT MANAGER
    # ---------------------------------------- #

    def close(self) -> None:
        """Closes the network connections
        """
        self.network.close()
        # XXX free game_handler?

    def __enter__(self) -> "Client":
        """Enters a context manager (with statement)

        Return value: Client
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
        return False
