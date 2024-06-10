"""Represents a network address

Classes:
    Address:
        Represents a network address
"""

import typing

from boomblazer.config.server import server_config

class Address(typing.NamedTuple):
    """Represents a network address

    Members:
        host: str
            The host part of the address
        port: int
            The port part of the address

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

        Parameters:
            address_repr: str
                The string representation of the address
                If the host part is empty, it will default to 0.0.0.0
                If the port part is empty, it will use the default value
                defined in the config variables

        Return value: Address
            The parsed Address
        """
        # We only want the last split in case the host part contains ":"
        address = address_repr.rsplit(":", 1)
        if len(address) == 1:
            address.append(server_config.default_port)
        address[1] = int(address[1])
        return cls(*address)

    def __str__(self) -> str:
        """Returns the string representation of the address

        Return value: str
            The string representation of the address
        """
        return f"{self.host}:{self.port}"
