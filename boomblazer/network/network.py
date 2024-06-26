"""Implements a network communication protocol for the game

Classes:
    Network:
        Base class for game network connection

Constants:
    _SEPARATOR: bytes
        The bytes sequence that separtes the command from its argument

Type aliases:
    MessageType:
        A message containing a command and an argument
"""

import logging
import socket
from collections.abc import Iterable
from typing import Optional

from boomblazer.network.address import Address

MessageType = tuple[bytes, bytes]  # (command, argument)

_SEPARATOR = b":"

class Network:
    """Base class for game network connection

    Members:
        sock: socket.socket
            Socket that handles the network communication with UDP
        _logger: logging.Logger
            Logger that registers network traffic

    Special methods:
        __init__:
            Initialize the Network object

    Methods:
        bind:
            Binds the network socket to a local address
        recv_message:
            Recieves a message from the network and parses it
        send_message:
            Constructs a message and sends it to the network
        close:
            Closes the network connection
    """

    __slots__ = ("sock", "_logger",)

    def __init__(self, logger: logging.Logger) -> None:
        """Initialize the Network object

        Parameters:
            logger: logging.Logger
                The network message logger
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._logger = logger

    def bind(self, addr: Address) -> None:
        """Binds the network socket to a local address

        Parameters:
            addr: Address
                The local address to bind the socket to
        """
        self.sock.bind(addr)

    def recv_message(self) -> tuple[Optional[MessageType], Address]:
        """Recieves a message from the network and parses it

        Return value: tuple[Optional[MessageType], Address]
            A message sent by the server and the IP address and port number
            from which the message was recieved.
            The message contains a command and an argument, or is `None` if the
            message was invalid
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
        """Constructs a message and sends it to the network

        Parameters:
            command: bytes
                The command to send to the server
            arg: bytes
                The argument associated to `command`
            peers: Iterable[Address]
                The peers at whom the message will be sent
        """
        msg = command + _SEPARATOR + arg
        for addr in peers:
            self._logger.info("[%s:%d] < %s", *addr, msg)
            self.sock.sendto(msg, addr)

    def close(self) -> None:
        """Closes the network connection
        """
        self.sock.close()
