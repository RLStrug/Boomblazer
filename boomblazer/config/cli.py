"""Command Line Interface configuration variables

Global variables:
    cli_config: _CLI_Config
        Singleton of _Config dataclass

Classes:
    _CLI_Config:
        Dataclass containing the CLI configuration values
"""


from typing import Iterable


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

cli_config=_CLI_Config()
