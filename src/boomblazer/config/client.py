"""Client configuration variables

Global variables:
    client_config: _ClientConfig
        Singleton of _ClientConfig dataclass
"""

from __future__ import annotations

import dataclasses
import typing

from .base_config import BaseConfig


@dataclasses.dataclass
class _ClientConfig(BaseConfig):
    """Dataclass containing the client configuration values

    Class constants:
        _DEFAULT_MAX_CONNECT_TRIES: int
            Default number of times the client will try to connect to the server
        _DEFAULT_MAX_CONNECT_WAIT: float
            Default waiting time for server connection answer

    Members:
        max_connect_tries: int
            Number of times the client will try to connect to the server
        max_connect_wait: float
            Waiting time for server connection answer
    """

    _DEFAULT_MAX_CONNECT_TRIES: typing.ClassVar[int] = 3
    _DEFAULT_MAX_CONNECT_WAIT: typing.ClassVar[float] = 1.0

    max_connect_tries: int = _DEFAULT_MAX_CONNECT_TRIES
    max_connect_wait: float = _DEFAULT_MAX_CONNECT_WAIT


client_config = _ClientConfig()
