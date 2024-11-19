"""Implements a game client"""

from __future__ import annotations

import enum
import io
import queue
import selectors
import socket
import struct
import typing

from ..config.client import client_config
from ..config.game import game_config
from ..environment.entity.player import PlayerAction
from ..environment.environment import Environment
from ..environment.map import Map
from ..environment.map import MapCell
from ..environment.position import Position
from ..environment.position import NULL_POSITION
from ..utils.repeater import Repeater
from .address import Address
from .client_info import ClientInfo
from .message import Message
from .network import Network
from .network import NULL_SOCKET

if typing.TYPE_CHECKING:
    import logging
    from collections.abc import Iterable
    from types import TracebackType
    from typing import Any
    from typing import Callable
    from typing import Self


class ClientError(Exception):
    """Exception thrown when an error occurs in the client"""


class ClientState(enum.Enum):
    """Represents the state of the game client"""

    DISCONNECTED = enum.auto()
    # CONNECTING = enum.auto()
    WAITING_IN_LOBBY = enum.auto()
    PLAYING = enum.auto()
    # SPECTATING = enum.auto()


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
        "server_socket": "(socket.socket) Server socket",
        "other_clients": "(dict[int, PlayerInfo]) Info of other clients connected to server",
        "selector": "selectors.DefaultSelector) Server socket read event listenner",
        "id": "(int) The client id number",
        "environment": "(Environment) Defines the current game environment",
        "state": "(ClientState) Current state of the client",
        "players_actions": "(queue.SimpleQueue) Players actions to perform",
        "display_environment": "(Callable[[Environment], None]) Function that will display environment each tick",
        "_tick_thread": "(threading.Thread) Thread that updates the game environment",
    }

    _SERVER_MESSAGE_WAIT_TIME = 0.5

    def __init__(
        self, display_environment: Callable[[Environment], None], logger: logging.Logger
    ) -> None:
        """Initializes a new Client

        :param server_addr: Address of the server hosting the game
        :param username: Name of the player
        """
        super().__init__(logger)
        self.server_socket = NULL_SOCKET
        self.other_clients: dict[int, ClientInfo] = {}
        self.environment = Environment()
        self.selector = selectors.DefaultSelector()
        self.id = -1
        self.players_actions: queue.SimpleQueue[dict[int, PlayerAction]] = (
            queue.SimpleQueue()
        )
        self.state = ClientState.DISCONNECTED

        self.display_environment = display_environment
        self._tick_thread = Repeater()

    # ---------------------------------------- #
    # GAME
    # ---------------------------------------- #

    def start(self) -> None:
        """Joins the server and sets up the reception af server packets"""
        while self.state is not ClientState.DISCONNECTED:
            if self.state is ClientState.WAITING_IN_LOBBY:
                self.wait_in_lobby()

            elif self.state is ClientState.PLAYING:
                for client_info in self.other_clients.values():
                    self.environment.spawn_player(
                        client_info.id, client_info.spawn_point
                    )

                self._tick_thread = Repeater(
                    interval=game_config.tick_frequency,
                    target=self.tick,
                    name="client-tick",
                )
                self._tick_thread.start()

                self.play_game()

                self._tick_thread.stop()
                self._tick_thread.join()

    def stop(self) -> None:
        """Stops client"""
        self.state = ClientState.DISCONNECTED

    def connect(self, address: Address, name: bytes) -> bool:
        """Connect to server"""
        assert self.server_socket is NULL_SOCKET
        try:
            self.server_socket = socket.create_connection(address)
        except ConnectionError:
            self.logger.exception(f"Cannot connect to {address}")
            return False

        self.state = ClientState.WAITING_IN_LOBBY
        self.selector.register(self.server_socket, selectors.EVENT_READ)
        self.send_name(name)

        return True

    def wait_in_lobby(self) -> None:
        """Recieves server messages during lobby state and updates clients info"""
        while self.state is ClientState.WAITING_IN_LOBBY:
            if not self.selector.select(self._SERVER_MESSAGE_WAIT_TIME):
                continue

            message_type_bytes = self.recv_from_server(1)

            if message_type_bytes == b"":
                self.state = ClientState.DISCONNECTED
                return

            message_type: int = struct.unpack("!B", message_type_bytes)[0]
            if message_type == Message.MAP:
                self.environment.load_map(self.recv_map())
                self.logger.info(f"Recieved game map: {str(self.environment.map)!r}")
                continue
            elif message_type == Message.LOBBY_INFO:
                self.other_clients = self.recv_lobby_info()
                self.logger.info(f"Recieved lobby info: {self.other_clients}")
                continue
            elif message_type == Message.START:
                self.state = ClientState.PLAYING  # TODO SPECTATING
                self.logger.info("Game start")
                return

            id_: int = struct.unpack("!B", self.recv_from_server(1))[0]
            if message_type == Message.ID:
                self.id = id_
                self.logger.info("Recieved id: %u", id_)
            elif message_type == Message.NAME:
                if id_ not in self.other_clients:
                    self.other_clients[id_] = ClientInfo(id_)
                name = self.recv_name()
                self.other_clients[id_].name = name
                self.logger.info("Client %u is named %s", id_, name)
            elif message_type == Message.SPAWN:
                spawn_point = self.recv_spawn()
                self.spawn_client(id_, spawn_point)
                self.logger.info("Client %u spawned at %s", id_, spawn_point)
            elif message_type == Message.DESPAWN:
                self.despawn_client(id_)
                self.logger.info("Client %u despawned", id_)
            elif message_type == Message.READY:
                self.other_clients[id_].is_ready = True
                self.logger.info("Client %u is ready", id_)
            elif message_type == Message.NOT_READY:
                self.other_clients[id_].is_ready = False
                self.logger.info("Client %u is not ready", id_)
            elif message_type == Message.DISCONNECT:
                self.despawn_client(id_)
                del self.other_clients[id_]
                self.logger.info("Client %u disconnected", id_)

    def play_game(self) -> None:
        """Recieves server messages during playing state and updates environment"""
        while self.state is ClientState.PLAYING:
            if not self.selector.select(self._SERVER_MESSAGE_WAIT_TIME):
                continue

            message_type_bytes = self.recv_from_server(1)

            if message_type_bytes == b"":
                self.state = ClientState.DISCONNECTED
                return

            message_type: int = struct.unpack("!B", message_type_bytes)[0]
            if message_type == Message.PLAYER_ACTIONS:
                players_actions = self.recv_players_actions()
                self.players_actions.put_nowait(players_actions)
                self.logger.info(f"Recieved players actions: {players_actions}")

    def tick(self, time: int) -> None:
        """Updates the game environment every time the server sends a message

        :param time: the time at which the function was called
        """
        if self.players_actions.empty():
            self.environment.tick({}, time)
        else:
            while not self.players_actions.empty():
                actions = self.players_actions.get_nowait()
                self.environment.tick(actions, time)
        self.display_environment(self.environment)

    # ---------------------------------------- #
    # NETWORK COMMUNICATIONS
    # ---------------------------------------- #

    def send_to_server(self, message: bytes) -> int:
        """Wrapper around Network.send that always sends to the server socket

        :param message: Message that should be sent
        :returns: How many bytes were sent
        """
        return self.send(self.server_socket, message)

    def recv_from_server(self, length: int) -> bytes:
        """Wrapper around Network.recv that always recieves from the server socket

        :param length: How many bytes should be recieved at most
        :returns: Message data
        """
        return self.recv(self.server_socket, length)

    # ---------------------------------------- #
    # SEND CLIENT COMMANDS
    # ---------------------------------------- #

    def send_name(self, name: bytes) -> None:
        """Send a NAME message to the server"""
        message = io.BytesIO()
        message.write(struct.pack("!B", Message.NAME))
        message.write(struct.pack("!B", len(name)))
        message.write(name)
        self.send_to_server(message.getvalue())

    def recv_name(self) -> bytes:
        """Recieve client name update"""
        name_length: int = struct.unpack("!B", self.recv_from_server(1))[0]
        name = self.recv_from_server(name_length)
        return name

    def send_spawn(self, spawn_point: Position) -> None:
        """Send a SPAWN message to the server"""
        message = struct.pack("!B BB", Message.SPAWN, spawn_point.x, spawn_point.y)
        self.send_to_server(message)

    def recv_spawn(self) -> Position:
        """Recieve client spawn point update"""
        x: int
        y: int
        x, y = struct.unpack("!BB", self.recv_from_server(2))
        spawn_point = Position(x, y)
        return spawn_point

    def spawn_client(self, id_: int, spawn_point: Position) -> None:
        """Set client spawn position"""
        self.despawn_client(id_)
        self.other_clients[id_].spawn_point = spawn_point
        self.environment.spawn_points.remove(spawn_point)

    def send_despawn(self) -> None:
        """Send a DESPAWN message to the server"""
        message = struct.pack("!B", Message.DESPAWN)
        self.send_to_server(message)

    def despawn_client(self, id_: int) -> None:
        """Recieve client despawn update"""
        spawn_point = self.other_clients[id_].spawn_point
        self.other_clients[id_].spawn_point = NULL_POSITION
        if spawn_point is not NULL_POSITION:
            self.environment.spawn_points.add(spawn_point)

    def send_ready(self) -> None:
        """Send a READY message to the server"""
        message = struct.pack("!B", Message.READY)
        self.send_to_server(message)

    def send_not_ready(self) -> None:
        """Send a NOT_READY message to the server"""
        message = struct.pack("!B", Message.NOT_READY)
        self.send_to_server(message)

    def recv_map(self) -> Map:
        """Recieve map data"""
        map_version: int = struct.unpack("!B", self.recv_from_server(1))[0]
        data_len: int = struct.unpack("!H", self.recv_from_server(2))[0]
        map_data = self.recv_from_server(data_len).decode("utf8")
        map_ = Map(
            map_version,
            [[MapCell(cell) for cell in row] for row in map_data.splitlines()],
        )
        return map_

    def recv_lobby_info(self) -> dict[int, ClientInfo]:
        """Recieve lobby info"""
        lobby_info: dict[int, ClientInfo] = {}
        nb_clients: int = struct.unpack("!B", self.recv_from_server(1))[0]
        for _ in range(nb_clients):
            id_: int
            name_length: int
            id_, name_length = struct.unpack("!BB", self.recv_from_server(2))
            name = self.recv_from_server(name_length)
            is_player: bool = struct.unpack("!?", self.recv_from_server(1))[0]
            if is_player:
                x: int
                y: int
                is_ready: bool
                skin: int
                x, y, is_ready, skin = struct.unpack(
                    "!BB ? B", self.recv_from_server(4)
                )
                spawn_point = Position(x, y)
            else:
                spawn_point = NULL_POSITION
                is_ready = False
                skin = 0
            lobby_info[id_] = ClientInfo(id_, name, spawn_point, is_ready, skin)
        return lobby_info

    def send_action(self, action: PlayerAction) -> None:
        """Send a PLAYER_ACTION message to the server"""
        message = struct.pack("!BB", Message.PLAYER_ACTIONS, action)
        self.send_to_server(message)

    def recv_players_actions(self) -> dict[int, PlayerAction]:
        """Recieve players' actions"""
        nb_actions: int = struct.unpack("!B", self.recv_from_server(1))[0]
        players_actions: dict[int, PlayerAction] = {}
        for _ in range(nb_actions):
            id_: int
            action: int
            id_, action = struct.unpack("!BB", self.recv_from_server(2))
            players_actions[id_] = PlayerAction(action)
        return players_actions

    # ---------------------------------------- #
    # CONTEXT MANAGER
    # ---------------------------------------- #

    # @override
    def close(self) -> None:
        """Closes the network connections"""
        self.server_socket.close()
        self.selector.close()

        self._tick_thread.stop()
        if self._tick_thread.ident is not None:
            self._tick_thread.join()
        self.logger.info("Client closing")
