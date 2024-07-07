"""Server configuration variables

Global variables:
    server_config: _ServerConfig
        Singleton of _ServerConfig dataclass

Classes:
    _ServerConfig:
        Dataclass containing the server configuration values
"""

import dataclasses
from typing import ClassVar

from .base_config import BaseConfig


@dataclasses.dataclass
class _ServerConfig(BaseConfig):
    """Dataclass containing the server configuration values

    Class constants:
        _DEFAULT_DEFAULT_INTERFACE: str
            The default value of the default server interface
        _DEFAULT_DEFAULT_PORT: int
            The default value of the default server port

    Members:
        default_interface: str
            The the default server interface
        default_port: int
            The default server port
    """

    _DEFAULT_DEFAULT_INTERFACE: ClassVar[str] = "0.0.0.0"
    _DEFAULT_DEFAULT_PORT: ClassVar[int] = 1337

    default_interface: str = _DEFAULT_DEFAULT_INTERFACE
    default_port: int = _DEFAULT_DEFAULT_PORT

server_config=_ServerConfig()
