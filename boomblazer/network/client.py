"""Implements a game client

Classes:
    Client:
        Implements client side of the network protocol
"""

import json
import selectors
import threading
from types import TracebackType
from typing import Iterable
from typing import Optional
from typing import Type

from boomblazer.config.client import client_config
from boomblazer.game_handler import GameHandler
from boomblazer.game_handler import MoveActionEnum
from boomblazer.map_environment import MapEnvironment
from boomblazer.network.network import AddressType
from boomblazer.network.network import Network


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

    Members:
        server_addr: AddressType
            The address of the remote game server
        is_host: bool
            Defines if this client is the host of the game
        username: str
            Defines the name of the player
        game_handler: GameHandler
            Defines the current game state
        is_game_running: bool
            Defines if the game is running or over
        _tick_thread: threading.Thread
            Thread used to update the game environment when a server packet is
            recieved
        update_semaphore: threading.semaphore
            Releases a token after each update recieved from the server. Its
            number of tokens should not exceed one in order to avoid
            overloading the underlying UI with updates if it somehow manages to
            be slower than network. Therefore, the Client should always try to
            acquire a token non-blockingly before releasing one.

    Special methods:
        __init__:
            Initializes a new Client
        __enter__:
            Enters a context manager (with statement)
        __exit__:
            Exits a context manager (with statement)

    Methods:
        start:
            Joins the server and sets up the reception af server packets
        tick:
            Updates the game environment every time the server sends a message
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
        "server_addr", "is_host", "username", "game_handler",
        "is_game_running", "_tick_thread", "update_semaphore",
    )

    _SERVER_MESSAGE_WAIT_TIME = 0.5

    def __init__(
            self, server_addr: AddressType, username: bytes,
            is_host: bool, *args, **kwargs
    ) -> None:
        """Initializes a new Client

        Parameters:
            server_addr: AddressType
                The IP address and port number of the server hosting the game
            username: str
                The name of the player
            is_host: bool
                Defines if this Client the game host
        """
        super().__init__(*args, **kwargs)
        self.server_addr = server_addr
        self.username = username
        self.is_host = is_host
        self.game_handler = GameHandler()
        self.is_game_running = False
        self._tick_thread = None
        self.update_semaphore = None

    # ---------------------------------------- #
    # GAME
    # ---------------------------------------- #

    def start(self) -> None:
        """Joins the server and sets up the reception af server packets
        """
        sel = selectors.DefaultSelector()
        sel.register(self.sock, selectors.EVENT_READ)

        for _ in range(client_config.max_connect_tries):
            self.send_join()
            events = sel.select(client_config.max_connect_wait)
            if not events:
                continue

            self.is_game_running = True
            self.update_semaphore = threading.Semaphore()
            self._logger.info(
                "Connected to %s:%d", self.server_addr[0], self.server_addr[1]
            )
            self._tick_thread = threading.Thread(
                target=self.tick, name="client-tick"
            )
            self._tick_thread.start()
            return

        # If connection failed
        self._logger.info(
            "Failed to connect to %s:%d",
            self.server_addr[0], self.server_addr[1]
        )

    def tick(self) -> None:
        """Updates the game environment every time the server sends a message
        """
        sel = selectors.DefaultSelector()
        sel.register(self.sock, selectors.EVENT_READ)

        while self.is_game_running:
            # Do not wait indefinitely in case game ended abruptly
            events = sel.select(self._SERVER_MESSAGE_WAIT_TIME)
            if not events:
                continue

            msg, addr = self.recv_message()
            if msg is None or addr != self.server_addr:
                continue

            cmd, arg = msg
            if cmd == b"PLAYERS_LIST":
                self.game_handler.map_environment.players = json.loads(arg)
            elif cmd == b"MAP":
                self.game_handler = GameHandler(
                    MapEnvironment.from_json(arg)
                )
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
            self, command: bytes, arg: bytes,
            peers: Optional[Iterable[AddressType]] = None
    ) -> None:
        """Sends a message to the server hosting the game

        Parameters:
            command: bytes
                The command to send to the server
            arg: bytes
                The argument associated to `command`
        """
        if peers is None:
            peers = (self.server_addr,)
        super().send_message(command, arg, peers)

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

    # @override
    def close(self) -> None:
        """Closes the network connections
        """
        self.is_game_running = False
        if self._tick_thread is not None:
            self._tick_thread.join()
        self.send_quit()
        super().close()

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
