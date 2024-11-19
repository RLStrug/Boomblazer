#!/usr/bin/env python3
"""Implements a game server"""

from __future__ import annotations

import argparse
import io
import pathlib
import logging
import selectors
import socket
import struct
import typing

from ..config.game import game_config
from ..config.game_folders import game_folders_config
from ..environment.entity.player import PlayerAction
from ..environment.environment import Environment
from ..environment.map import Map
from ..environment.map import MapError
from ..environment.map import NULL_MAP
from ..environment.position import Position
from ..environment.position import NULL_POSITION
from ..metadata import GAME_NAME
from ..utils.argument_parser import base_parser
from ..utils.argument_parser import handle_base_arguments
from ..utils.repeater import Repeater
from .address import Address
from .client_info import ClientInfo
from .message import Message
from .network import Network
from .network import NULL_SOCKET

if typing.TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Iterable
    from collections.abc import Sequence
    from collections.abc import Set
    from importlib.resources.abc import Traversable
    from typing import Any


class ServerError(Exception):
    """Exception thrown when an error occurs in the server"""


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
    """

    __slots__ = {
        "server_socket": "(socket.socket) Server socket that accepts clients",
        "connecting_clients": "(set[socket.socket]) Connecting clients sockets",
        "clients_sockets": "(dict[ClientInfo, socket.socket]) Connected clients sockets",
        "selector": "(selectors.DefaultSelector) sockets read event listenner",
        "environment": "(Environment) Game environment",
        "clients": "(dict[Address, Player]) Links connected players to their address",
        "is_running": "(bool) Defines if the server is running or over",
        "players_actions": "(dict[Player, PlayerAction]) Players actions for next tick",
        "_tick_thread": "(Repeater) Thread used to update the game environment",
    }

    _CLIENT_MESSAGE_WAIT_TIME = 0.5

    def __init__(self, logger: logging.Logger) -> None:
        """Initialize the Server object

        :param logger: Network message logger
        """
        super().__init__(logger)
        self.server_socket = NULL_SOCKET
        self.connecting_clients: set[socket.socket] = set()
        self.clients_sockets: dict[socket.socket, ClientInfo] = {}
        self.selector = selectors.DefaultSelector()
        self.is_running = False
        self.environment = Environment()

        self.players_actions: dict[int, PlayerAction] = {}
        self._tick_thread = Repeater()

    def bind(self, address: Address) -> None:
        """Binds the server to a port

        :param address: Interface and port on which the server will listen
        """
        self.server_socket = socket.create_server(
            address, family=socket.AF_INET6, dualstack_ipv6=socket.has_dualstack_ipv6()
        )
        self.selector.register(self.server_socket, selectors.EVENT_READ)
        self.logger.info(f"Server bound to {address}")

    def load_map_from_file(self, map_filename: str) -> None:
        """Loads the map from given file and initializes the environment

        :param map_filename: File containing the map environment initial data
        """
        map_filepath = self._find_map_file(map_filename)
        try:
            map_ = Map.from_file(map_filepath)
        except MapError as exc:
            raise ServerError(exc) from exc
        self.environment.load_map(map_)

    def _find_map_file(self, map_filename: str) -> Traversable:
        """Searches for map file in all folders defined in config

        Looks for map file in official maps folder first, then in custom maps folder.
        If the file is not found, return path to filename in current working directory

        :param map_filename: Map filename
        :returns: Map filepath
        """
        for maps_folder in game_folders_config.maps_folders:
            map_filepath = maps_folder / map_filename
            if map_filepath.is_file():
                return map_filepath
            self.logger.debug("%r not in %r", map_filename, str(maps_folder))
        # If file not in defined folders, try current working directory
        return pathlib.Path(".", map_filename)

    # ---------------------------------------- #
    # GAME STATE
    # ---------------------------------------- #

    def start(self) -> None:
        """Start the server

        Waits for the players and initializes the game map environment
        """
        assert self.server_socket is not NULL_SOCKET
        assert self.environment.map is not NULL_MAP
        self.is_running = True

        while self.is_running:
            self.await_players()

            if not self.is_running:
                break

            self.send_start()
            self.launch_game()
            if self._tick_thread.ident is not None:
                self._tick_thread.stop()
                self._tick_thread.join()

    def stop(self) -> None:
        """Stops the server"""
        self.is_running = False

    def await_players(self) -> None:
        """Waits for clients to connect until all players are ready"""
        self.logger.info("Waiting for players")
        ready_to_start = False
        while self.is_running and not ready_to_start:
            for key, _event in self.selector.select(self._CLIENT_MESSAGE_WAIT_TIME):
                # New client connection
                if key.fileobj is self.server_socket:
                    self.accept_connection()
                    continue

                client = key.fileobj
                assert isinstance(client, socket.socket)
                message_type_bytes = self.recv(client, 1)

                # Client disconnected
                if message_type_bytes == b"":
                    id_ = self.remove_client(client)
                    if id_ >= 0:
                        self.send_disconnect(id_)
                    continue

                # Do not convert to Message enum in case of invalid message type
                message_type: int = struct.unpack("!B", message_type_bytes)[0]

                # No command allowed until client gave his name
                if client in self.connecting_clients:
                    if message_type == Message.NAME:
                        id_ = self._generate_client_id()
                        self.clients_sockets[client] = ClientInfo(id_)
                        self.connecting_clients.remove(client)
                        self.send_id(client)
                        self.send_map(client)
                        self.send_lobby_info(client)
                    else:
                        continue

                if message_type == Message.NAME:
                    name = self.recv_name(client)
                    self.clients_sockets[client].name = name
                    self.send_name(client)

                elif message_type == Message.SPAWN:
                    spawn_point = self.recv_spawn(client)
                    if self.spawn_client(client, spawn_point):
                        self.send_spawn(client)

                elif self.clients_sockets[client].spawn_point is not NULL_POSITION:
                    if message_type == Message.READY:
                        self.clients_sockets[client].is_ready = True
                        self.send_ready(client)
                        ready_to_start = all(
                            client.is_ready
                            for client in self.clients_sockets.values()
                            if client.spawn_point is not NULL_POSITION
                        )
                    elif message_type == Message.NOT_READY:
                        self.clients_sockets[client].is_ready = False
                        self.send_not_ready(client)

                    elif message_type == Message.DESPAWN:
                        self.despawn_client(client)
                        self.send_despawn(client)

                # Ignore invalid messages types

    def _generate_client_id(self) -> int:
        """Generate client id

        :returns: The new client's id number
        """
        for id_ in range(len(self.clients_sockets)):
            if not any(
                id_ == client_info.id for client_info in self.clients_sockets.values()
            ):
                return id_
        return len(self.clients_sockets)

    def launch_game(self) -> None:
        """Runs the game logic from clients inputs

        Starts a thread that will update the game environment every tick
        Handles user input as they come on the main thread
        """
        self.logger.info("Game start")
        for client_info in self.clients_sockets.values():
            self.environment.spawn_player(client_info.id, client_info.spawn_point)

        self._tick_thread = Repeater(
            interval=game_config.tick_frequency, target=self.tick, name="server-tick"
        )
        self._tick_thread.start()

        self.handle_players_inputs()

        self._tick_thread.stop()
        self._tick_thread.join()
        # Should not stop game unless server is closing
        # self.send_stop_game(b"PLACEHOLDER wins")

    # ---------------------------------------- #
    # GAME
    # ---------------------------------------- #

    def tick(self, time: int) -> None:
        """Updates the game environment every tick and sends it to clients

        :param time: the time at which the function was called
        """
        if self.players_actions:  # If not empty
            self.send_players_actions()
        self.environment.tick(self.players_actions, time)
        self.players_actions = {}  # Reset TODO atomic op

    def handle_players_inputs(self) -> None:
        """Handle each player's action for current tick"""
        # Handle players input until there is no living player
        while self.is_running and len(self.environment.players) > 0:
            for key, _event in self.selector.select(self._CLIENT_MESSAGE_WAIT_TIME):
                client = key.fileobj
                assert isinstance(client, socket.socket)
                message_type_bytes = self.recv(client, 1)

                # Client disconnected
                if message_type_bytes == b"":
                    id_ = self.remove_client(client)
                    if id_ >= 0:
                        self.send_disconnect(id_)
                    continue

                client_info = self.clients_sockets.get(client)
                # We only want to treat messages from players
                if client_info is None or client_info.spawn_point is NULL_POSITION:
                    continue

                # Do not convert to Message enum in case of invalid message type
                message_type: int = struct.unpack("!B", message_type_bytes)[0]

                if message_type == Message.PLAYER_ACTIONS:
                    action = self.recv_player_actions(client)
                    self.players_actions[client_info.id] = action

    # ---------------------------------------- #
    # MESSAGE HANDLING
    # ---------------------------------------- #

    def accept_connection(self) -> None:
        """Accepts new client"""
        new_client, _ = self.server_socket.accept()
        self.connecting_clients.add(new_client)
        self.selector.register(new_client, selectors.EVENT_READ)
        self.logger.info(f"New connection {new_client.getpeername()}")

    def remove_client(self, client: socket.socket) -> int:
        """Disconnects client

        :param client: The socket of the client that should be removed
        :returns: True if the client had joined the lobby (i.e. sent a NAME)
        """
        self.selector.unregister(client)
        if client in self.connecting_clients:
            self.logger.info("Lost connection of unregistered client")
            del self.clients_sockets[client]
            return -1
        else:
            id_ = self.clients_sockets[client].id
            self.logger.info(f"Lost connection of client #{id_}")
            del self.clients_sockets[client]
            return id_

    def recv_name(self, client: socket.socket) -> bytes:
        """Recieves client name

        :param client: The socket of the client who sent the message
        :returns: The client's name
        """
        (name_length,) = struct.unpack("!B", self.recv(client, 1))
        name = self.recv(client, name_length)
        self.logger.info(f"{self.clients_sockets[client].id} is named {name!r}")
        return name

    def send_name(self, client: socket.socket) -> None:
        """Send new name of client to all clients

        :param client: The socket of the client who declared / changed name
        """
        id_ = self.clients_sockets[client].id
        name = self.clients_sockets[client].name
        self.send_to_all_clients(
            struct.pack("!BBB", Message.NAME, id_, len(name)) + name
        )

    def recv_spawn(self, client: socket.socket) -> Position:
        """Recieves player spawn point

        :param client: The socket of the client who sent the message
        :returns: The client's desired spawn position
        """
        x: int = struct.unpack("!B", self.recv(client, 1))[0]
        y: int = struct.unpack("!B", self.recv(client, 1))[0]
        spawn_point = Position(x, y)
        self.logger.info(
            f"Client #{self.clients_sockets[client].id} "
            f"wants to spawn at {spawn_point}"
        )
        return spawn_point

    def spawn_client(self, client: socket.socket, spawn_point: Position) -> bool:
        """Tries to spawn client at given point

        :param client: The socket of the client who wants a spawn point
        :param spawn_point: The client's desired spawn position
        :returns: True if spawn point is valid and available
        """
        if spawn_point not in self.environment.spawn_points:
            return False
        old_spawn_point = self.clients_sockets[client].spawn_point
        if old_spawn_point is not NULL_POSITION:
            self.environment.spawn_points.add(old_spawn_point)
        self.clients_sockets[client].spawn_point = spawn_point
        self.environment.spawn_points.remove(spawn_point)
        return True

    def send_spawn(self, client: socket.socket) -> None:
        """Send spawn position of client to all clients

        :param client: The socket of the client who sent the message
        """
        id_ = self.clients_sockets[client].id
        spawn_point = self.clients_sockets[client].spawn_point
        self.send_to_all_clients(
            struct.pack("!BBBB", Message.SPAWN, id_, spawn_point.x, spawn_point.y)
        )

    def despawn_client(self, client: socket.socket) -> None:
        """Despawn player and mark the old spawn point as available again

        :param client: The socket of the client who sent the message
        """
        spawn_point = self.clients_sockets[client].spawn_point
        self.environment.spawn_points.add(spawn_point)
        self.clients_sockets[client].spawn_point = NULL_POSITION
        self.logger.info(f"Client #{self.clients_sockets[client].id} despawned")

    def send_despawn(self, client: socket.socket) -> None:
        """Send client despawn message to all clients

        :param client: The socket of the client who released a spawn point
        """
        id_ = self.clients_sockets[client].id
        self.send_to_all_clients(struct.pack("!BB", Message.DESPAWN, id_))

    def send_ready(self, client: socket.socket) -> None:
        """Send client ready message to all clients

        :param client: The socket of the client who sent the message
        """
        id_ = self.clients_sockets[client].id
        self.send_to_all_clients(struct.pack("!BB", Message.READY, id_))

    def send_not_ready(self, client: socket.socket) -> None:
        """Send client despawn message to all clients

        :param client: The socket of the client who sent the message
        """
        id_ = self.clients_sockets[client].id
        self.send_to_all_clients(struct.pack("!BB", Message.NOT_READY, id_))

    def send_disconnect(self, id_: int) -> None:
        """Send client disconnect message to all clients

        :param id_: The id number of the client that disconnected
        """
        self.send_to_all_clients(struct.pack("!BB", Message.DISCONNECT, id_))

    def send_ok(self, client: socket.socket) -> None:
        """Tell client that is request was successful

        :param client: The socket of the client we will send the message to
        """
        self.send(client, struct.pack("!B", Message.OK))

    def send_nok(self, client: socket.socket) -> None:
        """Tell client that is request failed

        :param client: The socket of the client we will send the message to
        """
        self.send(client, struct.pack("!B", Message.NOK))

    def send_start(self) -> None:
        """Tell all clients the game is starting"""
        self.send_to_all_clients(struct.pack("!B", Message.START))

    def send_to_all_clients(self, message: bytes) -> None:
        """Send a message to all clients

        :param message: The message to send
        """
        for client in self.clients_sockets:
            self.send(client, message)

    def send_id(self, client: socket.socket) -> None:
        """Send its id number to a client

        :param client: The socket of the client we will send the message to
        """
        self.send(
            client,
            struct.pack("!BB", Message.ID, self.clients_sockets[client].id),
        )

    def send_map(self, client: socket.socket) -> None:
        """Send map data to a client

        :param client: The socket of the client we will send the message to
        """
        map_version = struct.pack("!B", self.environment.map.version)
        map_data = str(self.environment.map).encode("utf8")
        data_length = struct.pack("!H", len(map_data))
        self.send(
            client,
            struct.pack("!B", Message.MAP) + map_version + data_length + map_data,
        )

    def send_lobby_info(self, client: socket.socket) -> None:
        """Send lobby info to a client

        :param client: The socket of the client we will send the message to
        """
        lobby_info = io.BytesIO()
        nb_clients = struct.pack("!B", len(self.clients_sockets))
        for client_info in self.clients_sockets.values():
            lobby_info.write(struct.pack("!B", client_info.id))
            name_length = struct.pack("!B", len(client_info.name))
            lobby_info.write(name_length + client_info.name)

            if client_info.spawn_point is not NULL_POSITION:
                lobby_info.write(
                    struct.pack(
                        "!? BB ? B",
                        True,
                        client_info.spawn_point.x,
                        client_info.spawn_point.y,
                        client_info.is_ready,
                        client_info.skin,
                    )
                )
            else:
                lobby_info.write(struct.pack("!?", False))

        data = lobby_info.getvalue()
        message = struct.pack("!B", Message.LOBBY_INFO) + nb_clients + data
        self.send(client, message)

    def recv_player_actions(self, client: socket.socket) -> PlayerAction:
        """Recieves player actions

        :param client: The socket of the client who sent the message
        :returns: The player's action
        """
        action: int = struct.unpack("!B", self.recv(client, 1))[0]
        return PlayerAction(action)

    def send_players_actions(self) -> None:
        """Send players actions to all clients"""
        players_actions = io.BytesIO()
        nb_actions = struct.pack("!B", len(self.players_actions))
        for id_, action in self.players_actions.items():
            players_actions.write(struct.pack("!BB", id_, action))

        data = players_actions.getvalue()
        message = struct.pack("!B", Message.PLAYER_ACTIONS) + nb_actions + data
        self.send_to_all_clients(message)

    # ---------------------------------------- #
    # CONTEXT MANAGER
    # ---------------------------------------- #

    # @override
    def close(self) -> None:
        """Closes the server"""
        self.is_running = False
        if self._tick_thread.ident is not None:
            self._tick_thread.stop()
            self._tick_thread.join()
        self.logger.info("Server closing")


def main(argv: Sequence[str] | None = None) -> int:
    """Instanciates a Server

    :param argv: If None, uses command line arguments
    """
    parser = argparse.ArgumentParser(parents=[base_parser])
    parser.add_argument(
        "--address", metavar="[[HOST]:[PORT]]", type=Address.from_string, default=""
    )
    parser.add_argument("map_filename", type=pathlib.Path)
    args = parser.parse_args(argv)

    handle_base_arguments(args)
    logger = logging.getLogger(f"{GAME_NAME}.server")
    with Server(logger) as server:
        server.bind(args.address)
        server.load_map_from_file(args.map_filename)
        server.start()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
