"""Ncurses user interface configuration variables

Global variables:
    ncurses_config: _NcursesConfig
        Singleton of _Config dataclass

Classes:
    _NcursesConfig:
        Dataclass containing the ncurses UI configuration values
"""


import curses
from typing import Iterable


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


ncurses_config=_NcursesConfig()
