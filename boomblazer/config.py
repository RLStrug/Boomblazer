"""Game configuration variables

Global variables:
    config: _Config
        Singleton of _Config dataclass

Classes:
    _ServerConfig:
        Dataclass containing the server configuration values
    _ClientConfig:
        Dataclass containing the client configuration values
    _CLI_Config:
        Dataclass containing the CLI configuration values
    _NcursesConfig:
        Dataclass containing the ncurses UI configuration values
    _Config:
        Dataclass containing all the configuration values
"""


import curses
from typing import Iterable


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


class _CLI_Config:
    """Dataclass containing the CLI configuration values

    Class constants:
        _DEFAULT_UP_COMMANDS: Iterable[str]
            The default list of commands that move the player upwards
        _DEFAULT_DOWN_COMMANDS: Iterable[str]
            The default list of commands that move the player downwards
        _DEFAULT_LEFT_COMMANDS: Iterable[str]
            The default list of commands that move the player leftwards
        _DEFAULT_RIGHT_COMMANDS: Iterable[str]
            The default list of commands that move the player rightwards
        _DEFAULT_BOMB_COMMANDS: Iterable[str]
            The default list of commands that drop a bomb
        _DEFAULT_QUIT_COMMANDS: Iterable[str]
            The default list of commands that quit the game
        _DEFAULT_START_COMMANDS: Iterable[str]
            The default list of commands that start the game

    Members:
        up_commands: list[str]
            The list of commands that move the player upwards
        down_commands: list[str]
            The list of commands that move the player downwards
        left_commands: list[str]
            The list of commands that move the player leftwards
        right_commands: list[str]
            The list of commands that move the player rightwards
        bomb_commands: list[str]
            The list of commands that drop a bomb
        quit_commands: list[str]
            The list of commands that quit the game
        start_commands: list[str]
            The list of commands that start the game

    Special methods:
        __init__:
    """

    __slots__ = (
        "up_cmds", "down_cmds", "left_cmds", "right_cmds", "bomb_cmds",
        "quit_cmds", "start_cmds",
    )

    _DEFAULT_UP_COMMANDS = ("z", "up",)
    _DEFAULT_DOWN_COMMANDS = ("s", "down",)
    _DEFAULT_LEFT_COMMANDS = ("q", "left")
    _DEFAULT_RIGHT_COMMANDS = ("d", "right")
    _DEFAULT_BOMB_COMMANDS = ("b", "bomb",)
    _DEFAULT_QUIT_COMMANDS = ("Q", "quit", "exit", "stop",)
    _DEFAULT_START_COMMANDS = ("start",)

    def __init__(
            self, up_cmds: Iterable[str] = _DEFAULT_UP_COMMANDS,
            down_cmds: Iterable[str] = _DEFAULT_DOWN_COMMANDS,
            left_cmds: Iterable[str] = _DEFAULT_LEFT_COMMANDS,
            right_cmds: Iterable[str] = _DEFAULT_RIGHT_COMMANDS,
            bomb_cmds: Iterable[str] = _DEFAULT_BOMB_COMMANDS,
            quit_cmds: Iterable[str] = _DEFAULT_QUIT_COMMANDS,
            start_cmds: Iterable[str] = _DEFAULT_START_COMMANDS,
    ) -> None:
        self.up_cmds = list(up_cmds)
        self.down_cmds = list(down_cmds)
        self.left_cmds = list(left_cmds)
        self.right_cmds = list(right_cmds)
        self.bomb_cmds = list(bomb_cmds)
        self.quit_cmds = list(quit_cmds)
        self.start_cmds = list(start_cmds)

class _NcursesConfig:
    """Dataclass containing the ncurses UI configuration values

    Class constants:
        _DEFAULT_MENU_UP_BUTTONS: Iterable[int]
            The default list of buttons that move up in a menu
        _DEFAULT_MENU_DOWN_BUTTONS: Iterable[int]
            The default list of buttons that move down in a menu
        _DEFAULT_MENU_SELECT_BUTTONS: Iterable[int]
            The default list of buttons that select an option in a menu
        _DEFAULT_MOVE_UP_BUTTONS: Iterable[int]
            The default list of buttons that move the player upwards
        _DEFAULT_MOVE_DOWN_BUTTONS: Iterable[int]
            The default list of buttons that move the player downwards
        _DEFAULT_MOVE_LEFT_BUTTONS: Iterable[int]
            The default list of buttons that move the player leftwards
        _DEFAULT_MOVE_RIGHT_BUTTONS: Iterable[int]
            The default list of buttons that move the player rightwards
        _DEFAULT_DROP_BOMB_BUTTONS: Iterable[int]
            The default list of buttons that drop a bomb
        _DEFAULT_QUIT_BUTTONS: Iterable[int]
            The default list of buttons that quit the game

    Members:
        menu_up_buttons: list[int]
            The list of buttons that move up in a menu
        menu_down_buttons: list[int]
            The list of buttons that move down in a menu
        menu_select_buttons: list[int]
            The list of buttons that select an option in a menu
        move_up_buttons: list[int]
            The list of buttons that move the player upwards
        move_down_buttons: list[int]
            The list of buttons that move the player downwards
        move_left_buttons: list[int]
            The list of buttons that move the player leftwards
        move_right_buttons: list[int]
            The list of buttons that move the player rightwards
        drop_bomb_buttons: list[int]
            The list of buttons that drop a bomb
        quit_buttons: list[int]
            The list of buttons that quit the game
    """

    __slots__ = (
        "menu_up_buttons", "menu_down_buttons", "menu_select_buttons",
        "move_up_buttons", "move_down_buttons", "move_left_buttons",
        "move_right_buttons", "drop_bomb_buttons", "quit_buttons",
    )

    _DEFAULT_MENU_UP_BUTTONS = (curses.KEY_UP,)
    _DEFAULT_MENU_DOWN_BUTTONS = (curses.KEY_DOWN,)
    _DEFAULT_MENU_SELECT_BUTTONS = (ord('\n'),)
    _DEFAULT_MOVE_UP_BUTTONS = (ord("z"), curses.KEY_UP,)
    _DEFAULT_MOVE_DOWN_BUTTONS = (ord("s"), curses.KEY_DOWN,)
    _DEFAULT_MOVE_LEFT_BUTTONS = (ord("q"), curses.KEY_LEFT,)
    _DEFAULT_MOVE_RIGHT_BUTTONS = (ord("d"), curses.KEY_RIGHT,)
    _DEFAULT_DROP_BOMB_BUTTONS = (ord("b"), ord('\n'),)
    _DEFAULT_QUIT_BUTTONS = (ord("Q"),)

    def __init__(
            self, menu_up_buttons: Iterable[int] = _DEFAULT_MENU_UP_BUTTONS,
            menu_down_buttons: Iterable[int] = _DEFAULT_MENU_DOWN_BUTTONS,
            menu_select_buttons: Iterable[int] = _DEFAULT_MENU_SELECT_BUTTONS,
            move_up_buttons: Iterable[int] = _DEFAULT_MOVE_UP_BUTTONS,
            move_down_buttons: Iterable[int] = _DEFAULT_MOVE_DOWN_BUTTONS,
            move_left_buttons: Iterable[int] = _DEFAULT_MOVE_LEFT_BUTTONS,
            move_right_buttons: Iterable[int] = _DEFAULT_MOVE_RIGHT_BUTTONS,
            drop_bomb_buttons: Iterable[int] = _DEFAULT_DROP_BOMB_BUTTONS,
            quit_buttons: Iterable[int] = _DEFAULT_QUIT_BUTTONS
    ) -> None:
        self.menu_up_buttons = menu_up_buttons
        self.menu_down_buttons = menu_down_buttons
        self.menu_select_buttons = menu_select_buttons
        self.move_up_buttons = move_up_buttons
        self.move_down_buttons = move_down_buttons
        self.move_left_buttons = move_left_buttons
        self.move_right_buttons = move_right_buttons
        self.drop_bomb_buttons = drop_bomb_buttons
        self.quit_buttons = quit_buttons


class _Config:
    """Dataclass containing all the configuration values

    Members:
        server: _ServerConfig
            Server configuration variables
        client: _ClientConfig
            Client configuration variables
        cli: _CLI_Config
            Command line interface configuration variables
        ncurses: _NcursesConfig
            Ncurses user interface configuration variables

    Special methods:
        __init__:
            Initialize the configuration variables
    """

    __slots__ = ("server", "client", "cli", "ncurses",)

    def __init__(
            self, server: _ServerConfig, client: _ClientConfig,
            cli: _CLI_Config, ncurses: _NcursesConfig
    ) -> None:
        self.server = server
        self.client = client
        self.cli = cli
        self.ncurses = ncurses


config = _Config(
    server=_ServerConfig(),
    client=_ClientConfig(),
    cli=_CLI_Config(),
    ncurses=_NcursesConfig(),
)
