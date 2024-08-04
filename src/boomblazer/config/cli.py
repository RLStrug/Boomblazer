"""Command Line Interface configuration variables

Global variables:
    cli_config: _CLI_Config
        Singleton of _Config dataclass
"""

from __future__ import annotations

import dataclasses
import typing

from .base_config import BaseConfig
from .config_loader import config_instances

if typing.TYPE_CHECKING:
    from collections.abc import MutableSequence


@dataclasses.dataclass
class _CLI_Config(BaseConfig):
    """Dataclass containing the CLI configuration values

    Class constants:
        _DEFAULT_UP_COMMANDS: list[str]
            Default list of commands that move the player upwards
        _DEFAULT_DOWN_COMMANDS: list[str]
            Default list of commands that move the player downwards
        _DEFAULT_LEFT_COMMANDS: list[str]
            Default list of commands that move the player leftwards
        _DEFAULT_RIGHT_COMMANDS: list[str]
            Default list of commands that move the player rightwards
        _DEFAULT_BOMB_COMMANDS: list[str]
            Default list of commands that drop a bomb
        _DEFAULT_QUIT_COMMANDS: list[str]
            Default list of commands that quit the game
        _DEFAULT_READY_COMMANDS: list[str]
            Default list of commands that start the game

    Members:
        up_commands: MutableSequence[str]
            List of commands that move the player upwards
        down_commands: MutableSequence[str]
            List of commands that move the player downwards
        left_commands: MutableSequence[str]
            List of commands that move the player leftwards
        right_commands: MutableSequence[str]
            List of commands that move the player rightwards
        bomb_commands: MutableSequence[str]
            List of commands that drop a bomb
        quit_commands: MutableSequence[str]
            List of commands that quit the game
        ready_commands: MutableSequence[str]
            List of commands that start the game
    """

    _DEFAULT_UP_COMMANDS: typing.ClassVar[list[str]] = [
        "z",
        "up",
    ]
    _DEFAULT_DOWN_COMMANDS: typing.ClassVar[list[str]] = [
        "s",
        "down",
    ]
    _DEFAULT_LEFT_COMMANDS: typing.ClassVar[list[str]] = [
        "q",
        "left",
    ]
    _DEFAULT_RIGHT_COMMANDS: typing.ClassVar[list[str]] = [
        "d",
        "right",
    ]
    _DEFAULT_BOMB_COMMANDS: typing.ClassVar[list[str]] = [
        "b",
        "bomb",
    ]
    _DEFAULT_QUIT_COMMANDS: typing.ClassVar[list[str]] = [
        "Q",
        "quit",
        "exit",
        "stop",
    ]
    _DEFAULT_READY_COMMANDS: typing.ClassVar[list[str]] = [
        "ready",
        "start",
    ]

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


cli_config = _CLI_Config()
config_instances["cli"] = cli_config
