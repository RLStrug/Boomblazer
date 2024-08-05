"""Represents a network address

Global Constants:
    UNDEFINED_ADDRESS: Address
        Represents an undefined address
"""

import typing

from ..config.server import server_config


class Address(typing.NamedTuple):
    """Represents a network address

    Members:
        host: str
            Host part of the address
        port: int
            Port part of the address

    Class methods:
        from_string:
            Parses a string of format HOST:PORT into an Address

    Special methods:
        __str__:
            Returns the string representation of the address
    """

    host: str
    port: int

    @classmethod
    def from_string(cls, address_repr: str) -> "Address":
        """Parses a string of format HOST:PORT into an Address

        If the host part is empty, it will default to 0.0.0.0
        If the port part is empty, it will default to configured value

        :param address_repr: String representation of the address
        :returns: Parsed Address
        """
        # We only want the last split in case the host part contains ":"
        address = address_repr.rsplit(":", 1)
        host = address[0]
        if len(address) == 1:
            port = server_config.default_port
        else:
            port = int(address[1])
        return cls(host, port)

    def __str__(self) -> str:
        """Returns the string representation of the address

        :returns: String representation of the address
        """
        return f"{self.host}:{self.port}"


UNDEFINED_ADDRESS = Address("", 0)
