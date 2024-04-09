"""Server and game environment configuration variables

Global variables:
    server_config: _ServerConfig
        Singleton of _ServerConfig dataclass

Classes:
    _ServerConfig:
        Dataclass containing the server configuration values
"""


class _ServerConfig:
    """Dataclass containing the server configuration values

    Class constants:
        _DEFAULT_TICKS_PER_SECOND: int
            The default value for number of ticks per second
        _DEFAULT_BOMB_TIMER_SECONDS: float
            The default value for number of seconds before a bomb explodes
        _DEFAULT_FIRE_TIMER_SECONDS: float
            The default value for number of seconds before fire dissipates
        _DEFAULT_PLAYER_BOMB_COUNT: int
            The default number of bombs a player can drop at the same time
        _DEFAULT_PLAYER_BOMB_COUNT: int
            The default range of a bomb explosion blast

    Members:
        _ticks_per_second: int
            The number of ticks per second
        _tick_frequency: float
            The number of seconds between 2 ticks
        _bomb_timer_seconds: float
            The number of seconds before a bomb explodes
        _bomb_timer_ticks: int
            The number of ticks before a bomb explodes
        _fire_timer_seconds: float
            The number of seconds before a fire blast dissipates
        _fire_timer_ticks: int
            The number of ticks before a fire blast dissipates
        player_bomb_count: int
            The number of bombs a player can drop at the same time
        player_bomb_range: int
            The range of a bomb explosion blast

    Special methods:
        __init__:
            Initializes the dataclass

    Properties:
        ticks_per_second:
            The number of ticks per second
        tick_frequency (read-only):
            The number of seconds between 2 ticks
        bomb_timer_seconds:
            The number of seconds before a bomb explodes
        bomb_timer_ticks (read-only):
            The number of ticks before a bomb explodes
        fire_timer_seconds:
            The number of seconds before a fire blast dissipates
        fire_timer_ticks (read-only):
            The number of ticks before a fire blast dissipates
    """

    __slots__ = (
        "_ticks_per_second", "_tick_frequency", "_bomb_timer_seconds",
        "_bomb_timer_ticks", "_fire_timer_seconds", "_fire_timer_ticks",
        "player_bomb_count", "player_bomb_range",
    )

    _DEFAULT_TICKS_PER_SECOND = 60
    _DEFAULT_BOMB_TIMER_SECONDS = 3.0
    _DEFAULT_FIRE_TIMER_SECONDS = 1.0
    _DEFAULT_PLAYER_BOMB_COUNT = 1
    _DEFAULT_PLAYER_BOMB_RANGE = 2

    def __init__(
            self, ticks_per_second: int = _DEFAULT_TICKS_PER_SECOND,
            bomb_timer_seconds: float = _DEFAULT_BOMB_TIMER_SECONDS,
            fire_timer_seconds: float = _DEFAULT_FIRE_TIMER_SECONDS,
            player_bomb_count: int = _DEFAULT_PLAYER_BOMB_COUNT,
            player_bomb_range: int = _DEFAULT_PLAYER_BOMB_RANGE,
    ) -> None:
        """Initializes the dataclass

        _tick_frequency, _bomb_timer_ticks, and _fire_timer_ticks will be
        computed from given parameters

        Parameters:
            ticks_per_second:
                The number of ticks per second
            bomb_timer_seconds:
                The number of seconds before a bomb explodes
            fire_timer_seconds:
                The number of seconds before a fire blast dissipates
            player_bomb_count: int
                The number of bombs a player can drop at the same time
            player_bomb_range: int
                The range of a bomb explosion blast
        """
        self._ticks_per_second = ticks_per_second
        self._tick_frequency = 1 / ticks_per_second

        self._bomb_timer_seconds = bomb_timer_seconds
        self._bomb_timer_ticks = round(bomb_timer_seconds * ticks_per_second)

        self._fire_timer_seconds = fire_timer_seconds
        self._fire_timer_ticks = round(fire_timer_seconds * ticks_per_second)

        self.player_bomb_count = player_bomb_count
        self.player_bomb_range = player_bomb_range

    @property
    def ticks_per_second(self) -> int:
        """Returns the number of ticks per second

        Return value: int
            The number of ticks per second
        """
        return self._ticks_per_second

    @ticks_per_second.setter
    def ticks_per_second(self, ticks_per_second: int) -> None:
        """Sets the number of ticks per second

        Updates the number of ticks before bomb explosion or fire dissipating

        Parameters:
            ticks_per_second: int
                The new number of ticks per second
        """
        self._ticks_per_second = ticks_per_second
        self._tick_frequency = 1 / ticks_per_second
        self._bomb_timer_ticks = round(
            self._bomb_timer_seconds * ticks_per_second
        )
        self._fire_timer_ticks = round(
            self._fire_timer_seconds * ticks_per_second
        )

    @property
    def tick_frequency(self) -> float:
        """Returns the number of seconds between 2 ticks

        Return value: float
            The number of seconds between 2 ticks
        """
        return self._tick_frequency

    @property
    def bomb_timer_seconds(self) -> float:
        """Returns the number of seconds before a bomb explodes

        Return value: float
            The number of seconds before a bomb explodes
        """
        return self._bomb_timer_seconds

    @bomb_timer_seconds.setter
    def bomb_timer_seconds(self, bomb_timer_seconds: float) -> None:
        """Sets the number of seconds before a bomb explodes

        Updates the number of ticks before bomb explosion

        Parameters:
            bomb_timer_seconds: float
                The new number of seconds before a bomb explodes
        """
        self._bomb_timer_seconds = bomb_timer_seconds
        self._bomb_timer_ticks = round(
            bomb_timer_seconds * self._ticks_per_second
        )

    @property
    def bomb_timer_ticks(self) -> int:
        """Returns the number of ticks before a bomb explodes

        Return value: int
            The number of ticks before a bomb explodes
        """
        return self._bomb_timer_ticks

    @property
    def fire_timer_seconds(self) -> float:
        """Returns the number of seconds before a fire blast dissipates

        Return value: float
            The number of seconds before a fire blast dissipates
        """
        return self._fire_timer_seconds

    @fire_timer_seconds.setter
    def fire_timer_seconds(self, fire_timer_seconds: float) -> None:
        """Sets the number of seconds before a fire blast dissipates

        Updates the number of ticks before fire blast dissipating

        Parameters:
            fire_timer_seconds: float
                The new number of seconds before a fire blast dissipates
        """
        self._fire_timer_seconds = fire_timer_seconds
        self._fire_timer_ticks = round(
            fire_timer_seconds * self._ticks_per_second
        )

    @property
    def fire_timer_ticks(self) -> int:
        """Returns the number of ticks before a fire blast dissipates

        Return value: int
            The number of ticks before a fire blast dissipates
        """
        return self._fire_timer_ticks


server_config=_ServerConfig()
