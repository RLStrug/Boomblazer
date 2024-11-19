"""Implements a network communication protocol for the game

Constants:
    NULL_SOCKET: socket.socket
        Undefined socket
"""

from __future__ import annotations

import contextlib
import logging
import socket
import typing

if typing.TYPE_CHECKING:
    from collections.abc import Iterable
    from types import TracebackType
    from typing import Self


class Network:
    """Base class for game client and server"""

    __slots__ = {
        "logger": "(logging.Logger) Logger that registers network trafic",
    }

    def __init__(self, logger: logging.Logger) -> None:
        """Initialize the Network object

        :param logger: Network message logger
        """
        self.logger = logger

    def recv(self, sock: socket.socket, length: int) -> bytes:
        """Recieves a message from the network

        :param sock: Socket from which data should be recieved
        :param length: How many bytes should be recieved at most
        :returns: Message data
        """
        message = sock.recv(length)
        self.logger.debug("Recieving %s", message.hex())
        return message

    def send(self, sock: socket.socket, message: bytes) -> int:
        """Sends a message through the network

        Ignores ECONNRESET and EPIPE errors

        :param sock: Socket to which data should be sent
        :param message: Message that should be sent
        :returns: How many bytes were sent
        """
        self.logger.debug("Sending %s", message.hex())
        with contextlib.suppress(ConnectionResetError, BrokenPipeError):
            return sock.send(message)
        return 0

    def close(self) -> None:
        """Closes the network connection"""
        raise NotImplementedError

    def __enter__(self) -> Self:
        """Enters a context manager (with statement)

        :returns: The instance itself
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exits a context manager (with statement)

        :param exc_type: Type of the exception that occured during the context
        :param exc_val: Value of the exception that occured during the context
        :param exc_tb: Traceback of the exception that occured during the context
        :returns: None (exceptions are propagated)
        """
        self.close()


NULL_SOCKET = socket.socket()
