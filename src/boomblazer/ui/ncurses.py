#!/usr/bin/env python3
"""Implements a curses interface

This file can be run as a script.
"""

from __future__ import annotations

import argparse
import curses
import curses.ascii
import curses.textpad
import enum
import logging
import typing

from ..config.ncurses import ncurses_config
from ..environment.entity.player import PlayerAction
from ..environment.map import MapCell
from ..environment.position import Position
from ..environment.position import NULL_POSITION
from ..metadata import GAME_NAME
from ..network.address import Address
from ..network.client import ClientState
from ..utils.argument_parser import base_parser
from ..utils.argument_parser import handle_base_arguments
from ..utils.choice import Choice
from .base_ui import BaseUI

if typing.TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any
    from ..environment.environment import Environment


class MainMenuChoice(Choice):
    """Choices for the main menu"""

    JOIN = "Join a game"
    CREATE = "Create a game"
    EXIT = "Exit"


class JoinMenuChoice(Choice):
    """Choices for the join game menu"""

    ADDRESS = "Server address: "
    NAME = "Player name: "
    JOIN = "Join"
    EXIT = "Exit"


class CreateMenuChoice(Choice):
    """Choices for the create game menu"""

    GAME_MAP = "Game map: "
    NAME = "Player name: "
    CREATE = "Create"
    EXIT = "Exit"


class LobbyMenuChoice(Choice):
    """Choices for the lobby menu"""

    # NAME = "Change name"
    SPAWN = "Spawn"
    READY = "Ready"
    EXIT = "Exit"


class Color(enum.IntEnum):
    """Color index for ncurses"""

    DEFAULT = 0
    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    MAGENTA = 5
    CYAN = 6
    BLACK = 7
    WHITE = 8


NB_SKINS = 6  # red, blue, green, yellow, magenta, cyan


class CursesInterface(BaseUI):
    """A graphical terminal interface to play the game

    Class Constants:
        _INPUT_WAIT_TIME: int
            Number of miliseconds during which the UI waits for a key press
            before checking quickly if the game ended on abruptly.
            Ideally, this should not be 0.0 in order to avoid using 100% CPU
            for nothing. The value should not be too high either to avoid
            looking unresponsive to the user, even though the event should not
            happen often
    """

    __slots__ = {
        "stdscr": "(curses._CursesWindow) Screen controller",
    }

    _INPUT_WAIT_TIME = 500

    def __init__(self, stdscr: curses.window, *args: Any, **kwargs: Any) -> None:
        """Initiates the curses user interface

        :param stdscr: Screen controller
        """
        super().__init__(*args, **kwargs)
        self.stdscr = stdscr

    def main_menu(self) -> None:
        """Creates or joins the game and go to the lobby"""
        waiting = True
        current_choice = MainMenuChoice.JOIN
        while waiting:
            self.stdscr.clear()
            for choice in MainMenuChoice:
                attr = curses.A_NORMAL
                if current_choice is choice:
                    attr = curses.A_STANDOUT
                self.stdscr.insstr(choice.value, 0, choice.label, attr)

            key = self.stdscr.getch()
            if key in ncurses_config.menu_down_buttons:
                current_choice = current_choice.next
            elif key in ncurses_config.menu_up_buttons:
                current_choice = current_choice.previous
            elif key in ncurses_config.menu_select_buttons:
                waiting = False

        if current_choice is MainMenuChoice.JOIN:
            self.join_menu()
        elif current_choice is MainMenuChoice.CREATE:
            self.create_menu()

    def join_menu(self) -> None:
        """Gather server address then join"""
        waiting = True
        current_choice = JoinMenuChoice.ADDRESS
        textboxes = tuple(
            curses.textpad.Textbox(
                curses.newwin(1, curses.COLS, idx, len(choice.label))
            )
            for idx, choice in zip(range(2), JoinMenuChoice)
        )
        while waiting:
            self.stdscr.clear()
            for choice in JoinMenuChoice:
                attr = curses.A_NORMAL
                if current_choice is choice:
                    attr = curses.A_STANDOUT
                self.stdscr.insstr(choice.value, 0, choice.label, attr)
            for choice, textbox in zip(JoinMenuChoice, textboxes):
                self.stdscr.insstr(choice.value, len(choice.label), textbox.gather())
            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key in ncurses_config.menu_down_buttons:
                current_choice = current_choice.next
            elif key in ncurses_config.menu_up_buttons:
                current_choice = current_choice.previous
            elif key in ncurses_config.menu_select_buttons:
                if current_choice is JoinMenuChoice.JOIN:
                    waiting = False
                elif current_choice is JoinMenuChoice.EXIT:
                    return
                else:
                    curses.curs_set(1)  # Display cursor
                    textboxes[current_choice].edit()
                    curses.curs_set(0)  # Do not display cursor
                    current_choice = current_choice.next

        address = Address.from_string(
            textboxes[JoinMenuChoice.ADDRESS].gather().strip()
        )
        name = textboxes[JoinMenuChoice.NAME].gather().strip()

        self.stdscr.clear()
        self.stdscr.insstr(0, 0, f"Connecting to {address}")
        self.stdscr.refresh()

        self.join_game(address, name)
        if self.client.state is ClientState.WAITING_IN_LOBBY:
            self.lobby_menu()

    def create_menu(self) -> None:
        """Gather game map, username, creates server, and joins it"""
        waiting = True
        current_choice = CreateMenuChoice.GAME_MAP
        textboxes = tuple(
            curses.textpad.Textbox(
                curses.newwin(1, curses.COLS, idx, len(choice.label))
            )
            for idx, choice in zip(range(2), CreateMenuChoice)
        )
        while waiting:
            self.stdscr.clear()
            for choice in CreateMenuChoice:
                attr = curses.A_NORMAL
                if current_choice is choice:
                    attr = curses.A_STANDOUT
                self.stdscr.insstr(choice.value, 0, choice.label, attr)
            for choice, textbox in zip(CreateMenuChoice, textboxes):
                self.stdscr.insstr(choice.value, len(choice.label), textbox.gather())
            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key in ncurses_config.menu_down_buttons:
                current_choice = current_choice.next
            elif key in ncurses_config.menu_up_buttons:
                current_choice = current_choice.previous
            elif key in ncurses_config.menu_select_buttons:
                if current_choice is CreateMenuChoice.CREATE:
                    waiting = False
                elif current_choice is CreateMenuChoice.EXIT:
                    return
                else:
                    curses.curs_set(1)  # Display cursor
                    textboxes[current_choice].edit()
                    curses.curs_set(0)  # Do not display cursor
                    current_choice = current_choice.next

        # TODO Map chooser menu
        address = Address.from_string("")
        map_filename = textboxes[CreateMenuChoice.GAME_MAP].gather().strip()
        name = textboxes[CreateMenuChoice.NAME].gather().strip()

        self.stdscr.clear()
        self.stdscr.insstr(0, 0, f"Creating server on {address}")
        self.stdscr.refresh()

        self.create_game_and_join(address, name, map_filename)
        if self.client.state is ClientState.WAITING_IN_LOBBY:
            self.lobby_menu()

    def choose_spawn(self) -> Position:
        """Displays an interface to choose a spawn point"""
        spawn_points = [
            *self.client.environment.spawn_points,
            self.client.other_clients[self.client.id].spawn_point,
        ]
        choice_idx = len(spawn_points) - 1  # Current spawn point
        if self.client.other_clients[self.client.id].spawn_point is not NULL_POSITION:
            spawn_points.append(NULL_POSITION)

        if len(spawn_points) == 1:  # If no spawn point available
            return self.client.other_clients[self.client.id].spawn_point

        self.stdscr.timeout(-1)  # User input is blocking
        choosing = True
        while choosing:
            self.stdscr.clear()
            # Display map
            for row_idx, row in enumerate(self.client.environment.map):
                self.stdscr.move(row_idx, 0)
                for cell in row:
                    self.stdscr.addch(cell.value)
            # Display spawn points
            for spawn_idx, spawn_point in enumerate(spawn_points[:-1]):
                attr = curses.A_NORMAL
                if spawn_idx == choice_idx:
                    attr = curses.A_STANDOUT
                self.stdscr.addch(spawn_point.y, spawn_point.x, "S", attr)
            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key in ncurses_config.menu_down_buttons:
                choice_idx = (choice_idx + 1) % len(spawn_points)
            elif key in ncurses_config.menu_up_buttons:
                choice_idx = (choice_idx + len(spawn_points) - 1) % len(spawn_points)
            elif key in ncurses_config.menu_select_buttons:
                choosing = False

        self.stdscr.timeout(self._INPUT_WAIT_TIME)  # User input is non blocking
        return spawn_points[choice_idx]

    def lobby_menu(self) -> None:
        """Wait in lobby for everyone to be ready to start game"""
        current_choice = LobbyMenuChoice.SPAWN

        self.stdscr.timeout(self._INPUT_WAIT_TIME)  # User input is non blocking

        while self.client.state is ClientState.WAITING_IN_LOBBY:
            self.stdscr.clear()
            for idx, client_info in enumerate(self.client.other_clients.values()):
                skin = 0
                if client_info.spawn_point is not NULL_POSITION:
                    skin = (client_info.id % NB_SKINS) + 1
                ready_str = "X" if client_info.is_ready else " "
                self.stdscr.addstr(idx, 0, ready_str, curses.color_pair(skin))
                self.stdscr.addstr(f" {client_info.name.decode('utf8')}")

            first_choice_y_pos = curses.LINES - len(LobbyMenuChoice)
            for choice in LobbyMenuChoice:
                attr = curses.A_NORMAL
                if current_choice is choice:
                    attr = curses.A_STANDOUT
                self.stdscr.insstr(
                    first_choice_y_pos + choice.value, 0, choice.label, attr
                )

            key = self.stdscr.getch()
            if key == -1:
                continue

            if key in ncurses_config.menu_down_buttons:
                current_choice = current_choice.next
            elif key in ncurses_config.menu_up_buttons:
                current_choice = current_choice.previous
            elif key in ncurses_config.menu_select_buttons:
                if current_choice is LobbyMenuChoice.SPAWN:
                    spawn_point = self.choose_spawn()
                    if spawn_point != NULL_POSITION:
                        self.client.send_spawn(spawn_point)
                    else:
                        self.client.send_despawn()
                elif current_choice is LobbyMenuChoice.READY:
                    if self.client.other_clients[self.client.id].is_ready:
                        self.client.send_not_ready()
                    else:
                        self.client.send_ready()
                elif current_choice is LobbyMenuChoice.EXIT:
                    self.client.state = ClientState.DISCONNECTED
                    return

        self.play_game()
        self.stdscr.timeout(-1)  # User input is blocking

    def play_game(self) -> None:
        """Sends player actions and displays game state"""
        while self.client.state is ClientState.PLAYING:
            key = self.stdscr.getch()
            if key in ncurses_config.move_up_buttons:
                self.client.send_action(PlayerAction.MOVE_UP)
            elif key in ncurses_config.move_down_buttons:
                self.client.send_action(PlayerAction.MOVE_DOWN)
            elif key in ncurses_config.move_left_buttons:
                self.client.send_action(PlayerAction.MOVE_LEFT)
            elif key in ncurses_config.move_right_buttons:
                self.client.send_action(PlayerAction.MOVE_RIGHT)
            elif key in ncurses_config.drop_bomb_buttons:
                self.client.send_action(PlayerAction.PLANT_BOMB)
            elif key in ncurses_config.quit_buttons:
                self.client.state = ClientState.DISCONNECTED

    def display_environment(self, environment: Environment) -> None:
        """Displays the environment

        :param environment: The environment data
        """
        self.stdscr.erase()
        # Display map
        for row_idx, row in enumerate(self.client.environment.map):
            self.stdscr.move(row_idx, 0)
            for cell in row:
                if cell is MapCell.WALL:
                    self.stdscr.addch("#", curses.color_pair(Color.WHITE))
                elif cell is MapCell.BOX:
                    self.stdscr.addch("+", curses.color_pair(Color.WHITE))
                elif cell is MapCell.EMPTY:
                    self.stdscr.addch(" ", curses.color_pair(Color.BLACK))
                elif cell is MapCell.SPAWN:
                    self.stdscr.addch(" ", curses.color_pair(Color.BLACK))
        # Display players
        for player_id, player in environment.players.items():
            if player.position is NULL_POSITION:
                continue
            skin = curses.color_pair(player_id % NB_SKINS + 1)
            self.stdscr.addch(player.position.y, player.position.x, " ", skin)
        # Display bombs
        for bomb in environment.bombs:
            self.stdscr.addch(bomb.position.y, bomb.position.x, "o")
        # Display fire blasts
        for fire in environment.fires:
            self.stdscr.addch(fire.position.y, fire.position.x, "*")

        self.stdscr.refresh()


def init_colors() -> None:
    """Initializes curses color pairs"""
    if not curses.has_colors():
        return
    curses.init_pair(Color.RED, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(Color.BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(Color.GREEN, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(Color.YELLOW, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    curses.init_pair(Color.MAGENTA, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
    curses.init_pair(Color.CYAN, curses.COLOR_WHITE, curses.COLOR_CYAN)
    curses.init_pair(Color.BLACK, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(Color.WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)


def c_main(stdscr: curses.window, args: argparse.Namespace) -> int:
    """Launches the game

    :param stdscr: Screen controller
    :param args: Parsed arguments
    """
    curses.curs_set(0)  # Do not display cursor
    init_colors()

    handle_base_arguments(args)
    logger = logging.getLogger(f"{GAME_NAME}.ncurses")
    with CursesInterface(stdscr, logger=logger) as tui:
        tui.main_menu()

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Instanciates a curses interface

    :param argv: If None, uses command line arguments
    """
    parser = argparse.ArgumentParser(parents=[base_parser])
    args = parser.parse_args(argv)

    return curses.wrapper(c_main, args)


if __name__ == "__main__":
    raise SystemExit(main())
