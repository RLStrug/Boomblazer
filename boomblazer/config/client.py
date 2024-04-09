"""Client configuration variables

Global variables:
    client_config: _ClientConfig
        Singleton of _Config dataclass

Classes:
    _ClientConfig:
        Dataclass containing the client configuration values
"""


class _ClientConfig:
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

    Special methods:
        __init__:
            Initializes the dataclass
    """

    __slots__ = ("max_connect_tries", "max_connect_wait",)

    _DEFAULT_MAX_CONNECT_TRIES = 3
    _DEFAULT_MAX_CONNECT_WAIT = 1.0

    def __init__(
            self, max_connect_tries: int = _DEFAULT_MAX_CONNECT_TRIES,
            max_connect_wait: float = _DEFAULT_MAX_CONNECT_WAIT
    ) -> None:
        self.max_connect_tries = max_connect_tries
        self.max_connect_wait = max_connect_wait


client_config=_ClientConfig()
