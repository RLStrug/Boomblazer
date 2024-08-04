"""Ncurses user interface configuration variables

Global variables:
    ncurses_config: _NcursesConfig
        Singleton of _Config dataclass
"""

from __future__ import annotations

import curses
import dataclasses
import typing

from .base_config import BaseConfig
from .config_loader import config_instances

if typing.TYPE_CHECKING:
    from collections.abc import MutableSequence


@dataclasses.dataclass
class _NcursesConfig(BaseConfig):
    """Dataclass containing the ncurses UI configuration values

    Class constants:
        _DEFAULT_MENU_UP_BUTTONS: list[int]
            Default list of buttons that move up in a menu
        _DEFAULT_MENU_DOWN_BUTTONS: list[int]
            Default list of buttons that move down in a menu
        _DEFAULT_MENU_SELECT_BUTTONS: list[int]
            Default list of buttons that select an option in a menu
        _DEFAULT_MOVE_UP_BUTTONS: list[int]
            Default list of buttons that move the player upwards
        _DEFAULT_MOVE_DOWN_BUTTONS: list[int]
            Default list of buttons that move the player downwards
        _DEFAULT_MOVE_LEFT_BUTTONS: list[int]
            Default list of buttons that move the player leftwards
        _DEFAULT_MOVE_RIGHT_BUTTONS: list[int]
            Default list of buttons that move the player rightwards
        _DEFAULT_DROP_BOMB_BUTTONS: list[int]
            Default list of buttons that drop a bomb
        _DEFAULT_QUIT_BUTTONS: list[int]
            Default list of buttons that quit the game

    Members:
        menu_up_buttons: MutableSequence[int]
            List of buttons that move up in a menu
        menu_down_buttons: MutableSequence[int]
            List of buttons that move down in a menu
        menu_select_buttons: MutableSequence[int]
            List of buttons that select an option in a menu
        move_up_buttons: MutableSequence[int]
            List of buttons that move the player upwards
        move_down_buttons: MutableSequence[int]
            List of buttons that move the player downwards
        move_left_buttons: MutableSequence[int]
            List of buttons that move the player leftwards
        move_right_buttons: MutableSequence[int]
            List of buttons that move the player rightwards
        drop_bomb_buttons: MutableSequence[int]
            List of buttons that drop a bomb
        quit_buttons: MutableSequence[int]
            List of buttons that quit the game
    """

    _DEFAULT_MENU_UP_BUTTONS: typing.ClassVar[list[int]] = [
        curses.KEY_UP,
    ]
    _DEFAULT_MENU_DOWN_BUTTONS: typing.ClassVar[list[int]] = [
        curses.KEY_DOWN,
    ]
    _DEFAULT_MENU_SELECT_BUTTONS: typing.ClassVar[list[int]] = [
        ord("\n"),
    ]
    _DEFAULT_MOVE_UP_BUTTONS: typing.ClassVar[list[int]] = [
        ord("z"),
        curses.KEY_UP,
    ]
    _DEFAULT_MOVE_DOWN_BUTTONS: typing.ClassVar[list[int]] = [
        ord("s"),
        curses.KEY_DOWN,
    ]
    _DEFAULT_MOVE_LEFT_BUTTONS: typing.ClassVar[list[int]] = [
        ord("q"),
        curses.KEY_LEFT,
    ]
    _DEFAULT_MOVE_RIGHT_BUTTONS: typing.ClassVar[list[int]] = [
        ord("d"),
        curses.KEY_RIGHT,
    ]
    _DEFAULT_DROP_BOMB_BUTTONS: typing.ClassVar[list[int]] = [
        ord("b"),
        ord("\n"),
    ]
    _DEFAULT_QUIT_BUTTONS: typing.ClassVar[list[int]] = [
        ord("Q"),
    ]

    menu_up_buttons: MutableSequence[int] = dataclasses.field(
        default_factory=_DEFAULT_MENU_UP_BUTTONS.copy
    )
    menu_down_buttons: MutableSequence[int] = dataclasses.field(
        default_factory=_DEFAULT_MENU_DOWN_BUTTONS.copy
    )
    menu_select_buttons: MutableSequence[int] = dataclasses.field(
        default_factory=_DEFAULT_MENU_SELECT_BUTTONS.copy
    )
    move_up_buttons: MutableSequence[int] = dataclasses.field(
        default_factory=_DEFAULT_MOVE_UP_BUTTONS.copy
    )
    move_down_buttons: MutableSequence[int] = dataclasses.field(
        default_factory=_DEFAULT_MOVE_DOWN_BUTTONS.copy
    )
    move_left_buttons: MutableSequence[int] = dataclasses.field(
        default_factory=_DEFAULT_MOVE_LEFT_BUTTONS.copy
    )
    move_right_buttons: MutableSequence[int] = dataclasses.field(
        default_factory=_DEFAULT_MOVE_RIGHT_BUTTONS.copy
    )
    drop_bomb_buttons: MutableSequence[int] = dataclasses.field(
        default_factory=_DEFAULT_DROP_BOMB_BUTTONS.copy
    )
    quit_buttons: MutableSequence[int] = dataclasses.field(
        default_factory=_DEFAULT_QUIT_BUTTONS.copy
    )


ncurses_config = _NcursesConfig()
config_instances["ncurses"] = ncurses_config
