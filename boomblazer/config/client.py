"""Client configuration variables

Global variables:
    client_config: _ClientConfig
        Singleton of _ClientConfig dataclass

Classes:
    _ClientConfig:
        Dataclass containing the client configuration values
"""


import dataclasses
from typing import ClassVar

from boomblazer.config.base_config import BaseConfig
from boomblazer.config.config_loader import config_instances


@dataclasses.dataclass(slots=True)
class _ClientConfig(BaseConfig):
    """Dataclass containing the client configuration values

    Class constants:
        _DEFAULT_MAX_CONNECT_TRIES: int
            The default number of times a client should try connecting to a
            server
        _DEFAULT_MAX_CONNECT_WAIT: float
            The default number of seconds a client should wait for server
            answer before trying again to connect or giving up

    Members:
        max_connect_tries: int
            The number of times a client should try connecting to a server
        max_connect_wait: float
            The number of seconds a client should wait for server answer before
            trying again to connect or giving up
    """

    _DEFAULT_MAX_CONNECT_TRIES: ClassVar[int] = 3
    _DEFAULT_MAX_CONNECT_WAIT: ClassVar[float] = 1.0

    max_connect_tries: int = _DEFAULT_MAX_CONNECT_TRIES
    max_connect_wait: float = _DEFAULT_MAX_CONNECT_WAIT


client_config=_ClientConfig()
config_instances["client"] = client_config
