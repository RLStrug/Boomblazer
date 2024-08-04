"""Server configuration variables

Global variables:
    server_config: _ServerConfig
        Singleton of _ServerConfig dataclass
"""

from __future__ import annotations

import dataclasses
import typing

from .base_config import BaseConfig


@dataclasses.dataclass
class _ServerConfig(BaseConfig):
    """Dataclass containing the server configuration values

    Class constants:
        _DEFAULT_DEFAULT_INTERFACE: str
            Default value of the default server interface
        _DEFAULT_DEFAULT_PORT: int
            Default value of the default server port

    Members:
        default_interface: str
            Default server interface
        default_port: int
            Default server port
    """

    _DEFAULT_DEFAULT_INTERFACE: typing.ClassVar[str] = "0.0.0.0"
    _DEFAULT_DEFAULT_PORT: typing.ClassVar[int] = 1337

    default_interface: str = _DEFAULT_DEFAULT_INTERFACE
    default_port: int = _DEFAULT_DEFAULT_PORT


server_config = _ServerConfig()
