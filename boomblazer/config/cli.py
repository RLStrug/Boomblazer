"""Command Line Interface configuration variables

Global variables:
    cli_config: _CLI_Config
        Singleton of _Config dataclass

Classes:
    _CLI_Config:
        Dataclass containing the CLI configuration values
"""


import dataclasses
from typing import ClassVar
from typing import List
from typing import MutableSequence

from boomblazer.config.base_config import BaseConfig
from boomblazer.config.config_loader import config_instances


@dataclasses.dataclass(slots=True)
class _CLI_Config(BaseConfig):
    """Dataclass containing the CLI configuration values

    Class constants:
        _DEFAULT_UP_COMMANDS: list[str]
            The default list of commands that move the player upwards
        _DEFAULT_DOWN_COMMANDS: list[str]
            The default list of commands that move the player downwards
        _DEFAULT_LEFT_COMMANDS: list[str]
            The default list of commands that move the player leftwards
        _DEFAULT_RIGHT_COMMANDS: list[str]
            The default list of commands that move the player rightwards
        _DEFAULT_BOMB_COMMANDS: list[str]
            The default list of commands that drop a bomb
        _DEFAULT_QUIT_COMMANDS: list[str]
            The default list of commands that quit the game
        _DEFAULT_READY_COMMANDS: list[str]
            The default list of commands that start the game

    Members:
        up_commands: MutableSequence[str]
            The list of commands that move the player upwards
        down_commands: MutableSequence[str]
            The list of commands that move the player downwards
        left_commands: MutableSequence[str]
            The list of commands that move the player leftwards
        right_commands: MutableSequence[str]
            The list of commands that move the player rightwards
        bomb_commands: MutableSequence[str]
            The list of commands that drop a bomb
        quit_commands: MutableSequence[str]
            The list of commands that quit the game
        ready_commands: MutableSequence[str]
            The list of commands that start the game
    """

    _DEFAULT_UP_COMMANDS: ClassVar[List[str]] = ["z", "up",]
    _DEFAULT_DOWN_COMMANDS: ClassVar[List[str]] = ["s", "down",]
    _DEFAULT_LEFT_COMMANDS: ClassVar[List[str]] = ["q", "left"]
    _DEFAULT_RIGHT_COMMANDS: ClassVar[List[str]] = ["d", "right"]
    _DEFAULT_BOMB_COMMANDS: ClassVar[List[str]] = ["b", "bomb",]
    _DEFAULT_QUIT_COMMANDS: ClassVar[List[str]] = ["Q", "quit", "exit", "stop",]
    _DEFAULT_READY_COMMANDS: ClassVar[List[str]] = ["ready", "start",]

    up_commands: MutableSequence[str] = dataclasses.field(
        default_factory=_DEFAULT_UP_COMMANDS.copy
    )
    down_commands: MutableSequence[str] = dataclasses.field(
        default_factory=_DEFAULT_DOWN_COMMANDS.copy
    )
    left_commands: MutableSequence[str] = dataclasses.field(
        default_factory=_DEFAULT_LEFT_COMMANDS.copy
    )
    right_commands: MutableSequence[str] = dataclasses.field(
        default_factory=_DEFAULT_RIGHT_COMMANDS.copy
    )
    bomb_commands: MutableSequence[str] = dataclasses.field(
        default_factory=_DEFAULT_BOMB_COMMANDS.copy
    )
    quit_commands: MutableSequence[str] = dataclasses.field(
        default_factory=_DEFAULT_QUIT_COMMANDS.copy
    )
    ready_commands: MutableSequence[str] = dataclasses.field(
        default_factory=_DEFAULT_READY_COMMANDS.copy
    )


cli_config=_CLI_Config()
config_instances["cli"] = cli_config
