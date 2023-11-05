"""Implements a game map environment

Classes:
    Network:
        Game network protocol

Constants:
    _SEPARATOR: bytes
        The bytes sequence that separtes the command from its argument

Type aliases:
    MessageType:
        A message containing a command and an argument
    AddressType:
        An address coposed of an IP and a port number
"""

import logging
import socket
from typing import Iterable
from typing import Optional
from typing import Tuple

MessageType = Tuple[bytes, bytes]  # (command, argument)
AddressType = Tuple[str, int]  # (address, port)

_SEPARATOR = b":"

class Network:
    """Game network protocol

    Members:
        sock: socket.socket
            Socket that handles the network communication with UDP
        _logger: logging.Logger
            Logger that registers network traffic

    Special methods:
        __init__:
            Initialize the Network object

    Methods:
        recv_message:
            Recieves a message from the network and parses it
        send_message:
            Constructs a message and sends it to the network
        close:
            Closes the network connection
    """

    __slots__ = ("sock", "_logger",)

    def __init__(
            self, logger: logging.Logger, *,
            bind_addr: Optional[AddressType] = None
    ) -> None:
        """Initialize the Network object

        Parameters:
            logger: logging.Logger
                the network message logger

        Keyword only parameters:
            bind_addr: Optional[AddressType]
                If this is the server, specifies at which address it should be
                binded
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._logger = logger

        if bind_addr is not None:
            self.sock.bind(bind_addr)

    def recv_message(self) -> Tuple[Optional[MessageType], AddressType]:
        """Recieves a message from the network and parses it

        Return value: tuple[Optional[MessageType], AddressType]
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

    def send_message(self, command: bytes, arg: bytes,
            peers: Iterable[AddressType]) -> None:
        """Constructs a message and sends it to the network

        Parameters:
            command: bytes
                The command to send to the server
            arg: bytes
                The argument associated to `command`
            peers: Iterable[AddressType]
                The peers at whom the message will be sent
        """
        msg = command + _SEPARATOR + arg
        for addr in peers:
            self._logger.info("[%s:%d] < %s", *addr, msg)
            self.sock.sendto(msg, addr)

    def close(self) -> None:
        """Closes the network connection"""
        self.sock.close()
