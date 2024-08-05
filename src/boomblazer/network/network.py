"""Implements a network communication protocol for the game

Constants:
    _SEPARATOR: bytes
        The bytes sequence that separtes the command from its argument

Type aliases:
    MessageType:
        A message containing a command and an argument
"""

from __future__ import annotations

import logging
import selectors
import socket
import typing

from .address import Address

if typing.TYPE_CHECKING:
    from collections.abc import Iterable

MessageType = tuple[bytes, bytes]  # (command, argument)

_SEPARATOR = b":"


class Network:
    """Base class for game network connection"""

    __slots__ = {
        "sock": "(socket.socket) Socket that handles network communication with UDP",
        "selector": "(selectors.DefaultSelector) Listenner for network message",
        "_logger": "(logging.Logger) Logger that registers network traffic",
    }

    def __init__(self, logger: logging.Logger) -> None:
        """Initialize the Network object

        :param logger: Network message logger
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.sock, selectors.EVENT_READ)
        self._logger = logger

    def bind(self, addr: Address) -> None:
        """Binds the network socket to a local address

        :param addr: Local address to bind the socket to
        """
        self.sock.bind(addr)

    def recv_message(self) -> tuple[MessageType | None, Address]:
        """Recieves a message from the network and parses it

        :returns: Message and Address of sender
        """
        msg, addr = self.sock.recvfrom(65536)
        self._logger.info("[%s:%d] > %s", *addr, msg)
        if _SEPARATOR not in msg:
            return None, addr
        command, arg = msg.split(_SEPARATOR, 1)
        return (command, arg), addr

    def send_message(
        self, command: bytes, arg: bytes, peers: Iterable[Address]
    ) -> None:
        """Constructs a message and sends it through the network

        :param command: Command to send
        :param arg: Argument associated to `command`
        :param peers: Peers at whom the message will be sent
        """
        msg = command + _SEPARATOR + arg
        for addr in peers:
            self._logger.info("[%s:%d] < %s", *addr, msg)
            self.sock.sendto(msg, addr)

    def close(self) -> None:
        """Closes the network connection"""
        self.sock.close()
        self.selector.close()
