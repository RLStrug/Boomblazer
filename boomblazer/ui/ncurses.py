#!/usr/bin/env python3
"""Implements a curses interface

This file can be run as a script.

Classes:
    CursesInterface: BaseUI
        A curses interface to play the game

Functions:
    main:
        Instanciates a curses interface and launches the game
"""

import argparse
import curses
import curses.ascii
import curses.textpad
import enum
import logging
import pathlib
import sys
from collections.abc import Sequence
from typing import Optional

from boomblazer.argument_parser import base_parser
from boomblazer.argument_parser import handle_base_arguments
from boomblazer.config.ncurses import ncurses_config
from boomblazer.environment.entity.player import PlayerAction
from boomblazer.network.address import Address
from boomblazer.ui.base_ui import BaseUI
from boomblazer.version import GAME_NAME


class CursesInterface(BaseUI):
    """A command line interface to play the game

    Special methods:
        __init__:
            Initiates the command line user interface

    Members:
        stdscr: curses._CursesWindow
            The screen controller

    Methods:
        main_menu:
            Creates or joins the game and go to the lobby
        join_menu:
            Gather server url and port then join
        create_menu:
            Gather server port, game map, username, creates server, and joins it
        play_game:
            Sends player actions and displays game state
        handle_user_input:
            Sends user input to server as player actions
        handle_network_input:
            Recieves game info from the server
    """

    __slots__ = ("stdscr",)

    def __init__(self, stdscr: curses.window, *args, **kwargs) -> None:
        """Initiates the curses user interface

        Parameters:
        stdscr: curses._CursesWindow
            The screen controller
        """
        super().__init__(*args, **kwargs)
        self.stdscr = stdscr

    def main_menu(self) -> None:
        """Creates or joins the game and go to the lobby
        """
        waiting = True
        choices = enum.IntEnum(
            "MainMenuChoiceEnum",
            "JOIN CREATE EXIT",
            start=0
        )
        current_choice = choices(0)
        labels = (
            "Join a game", "Create a game", "Exit"
        )
        while waiting:
            self.stdscr.clear()
            for idx, label in enumerate(labels):
                self.stdscr.insstr(idx, 0, label,
                    curses.A_STANDOUT if current_choice is choices(idx)
                    else curses.A_NORMAL)

            key = self.stdscr.getch()
            new_choice = int(current_choice)
            if key in ncurses_config.menu_down_buttons:
                new_choice += 1
            elif key in ncurses_config.menu_up_buttons:
                new_choice += len(choices) - 1
            elif key in ncurses_config.menu_select_buttons:
                waiting = False
            current_choice = choices(new_choice % len(choices))

        if current_choice is choices.JOIN:
            self.join_menu()
        elif current_choice is choices.CREATE:
            self.create_menu()

    def join_menu(self) -> None:
        """Gather server address then join
        """
        waiting = True
        choices = enum.IntEnum(
            "JoinMenuChoiceEnum",
            "ADDRESS NAME JOIN EXIT",
            start=0
        )
        current_choice = choices(0)
        labels = (
            "Server address:", "Player name:", "Join", "Exit",
        )
        textboxes = tuple(
            curses.textpad.Textbox(curses.newwin(
                1, curses.COLS, idx, len(labels[idx]) + 1))
            for idx in range(2)
        )
        while waiting:
            self.stdscr.clear()
            for idx, label in enumerate(labels):
                self.stdscr.insstr(idx, 0, label,
                    curses.A_STANDOUT if current_choice is choices(idx)
                    else curses.A_NORMAL)
            for idx, (label, textbox) in enumerate(zip(labels, textboxes)):
                self.stdscr.insstr(idx, len(label) + 1, textbox.gather())
            self.stdscr.refresh()

            key = self.stdscr.getch()
            new_choice = int(current_choice)
            if key in ncurses_config.menu_down_buttons:
                new_choice += 1
            elif key in ncurses_config.menu_up_buttons:
                new_choice += len(choices) - 1
            elif key in ncurses_config.menu_select_buttons:
                if current_choice is choices.JOIN:
                    waiting = False
                elif current_choice is choices.EXIT:
                    return
                else:
                    curses.curs_set(1)  # Display cursor
                    textboxes[current_choice].edit()
                    curses.curs_set(0)  # Do not display cursor
                    new_choice += 1
            current_choice = choices(new_choice % len(choices))

        address = Address.from_string(
                textboxes[choices.ADDRESS].gather().strip()
        )
        name = textboxes[choices.NAME].gather().strip()

        self.stdscr.clear()
        self.stdscr.insstr(0, 0, f"Connecting to {address}")
        self.stdscr.refresh()

        self.join_game(address, name)
        if self.client.is_game_running:
            self.lobby_menu()

    def create_menu(self) -> None:
        """Gather game map, username, creates server, and joins it
        """
        waiting = True
        choices = enum.IntEnum(
            "JoinMenuChoiceEnum",
            "MAP NAME JOIN EXIT",
            start=0
        )
        current_choice = choices(0)
        labels = (
            "Game map:", "Player name:", "Create", "Exit",
        )
        textboxes = tuple(
            curses.textpad.Textbox(curses.newwin(
                1, curses.COLS, idx, len(labels[idx]) + 1))
            for idx in range(2)
        )
        while waiting:
            self.stdscr.clear()
            for idx, label in enumerate(labels):
                self.stdscr.insstr(idx, 0, label,
                    curses.A_STANDOUT if current_choice is choices(idx)
                    else curses.A_NORMAL)
            for idx, (label, textbox) in enumerate(zip(labels, textboxes)):
                self.stdscr.insstr(idx, len(label) + 1, textbox.gather())
            self.stdscr.refresh()

            key = self.stdscr.getch()
            new_choice = int(current_choice)
            if key in ncurses_config.menu_down_buttons:
                new_choice += 1
            elif key in ncurses_config.menu_up_buttons:
                new_choice += len(choices) - 1
            elif key in ncurses_config.menu_select_buttons:
                if current_choice is choices.JOIN:
                    waiting = False
                elif current_choice is choices.EXIT:
                    return
                else:
                    curses.curs_set(1)  # Display cursor
                    textboxes[current_choice].edit()
                    curses.curs_set(0)  # Do not display cursor
                    new_choice += 1
            current_choice = choices(new_choice % len(choices))

        # TODO Map chooser menu
        address = Address.from_string("")
        map_filename = textboxes[choices.MAP].gather().strip()
        name = textboxes[choices.NAME].gather().strip()

        self.stdscr.clear()
        self.stdscr.insstr(0, 0, f"Creating server on {address}")
        self.stdscr.refresh()

        self.create_game_and_join(address, name, map_filename)
        if self.client.is_game_running:
            self.lobby_menu()

    def lobby_menu(self) -> None:
        """Wait in lobby for everyone to be ready to start game
        """
        need_redraw = True
        choices = enum.IntEnum(
            "LobbyMenuChoiceEnum",
            "READY EXIT",
            start=0
        )
        labels = ("Ready", "Exit",)
        current_choice = choices(0)

        self.stdscr.nodelay(True)  # User input is non blocking

        while self.client.environment.map.version == 0:
            if need_redraw:
                need_redraw = False
                self.stdscr.clear()
                for idx, (player, is_ready) in enumerate(
                        self.client.connected_players.items()
                ):
                    self.stdscr.insstr(idx, 0, f"{player}")
                    if is_ready:
                        self.stdscr.insstr(idx, len(player), " (ready)")
                for idx, label in enumerate(labels):
                    self.stdscr.insstr(
                        curses.LINES - len(choices) + idx, 0, label,
                        curses.A_STANDOUT if current_choice is choices(idx)
                        else curses.A_NORMAL
                    )

            key = self.stdscr.getch()
            if key != -1:
                need_redraw = True

            new_choice = int(current_choice)
            if key in ncurses_config.menu_down_buttons:
                new_choice += 1
            elif key in ncurses_config.menu_up_buttons:
                new_choice += len(choices) - 1
            elif key in ncurses_config.menu_select_buttons:
                if current_choice is choices.EXIT:
                    return
                self.client.send_ready()
            current_choice = choices(new_choice % len(choices))

            if self.client.update_semaphore.acquire(blocking=False):
                need_redraw = True
            if not self.client.is_game_running:
                return
        self.play_game()
        self.stdscr.nodelay(False)  # User input is blocking


    def play_game(self) -> None:
        """Sends player actions and displays game state
        """
        need_redraw = True

        while self.client.is_game_running:
            if need_redraw:
                need_redraw = False
                self.stdscr.clear()
                self.stdscr.insstr(0, 0, str(self.client.environment))

            key = self.stdscr.getch()
            if key in ncurses_config.move_up_buttons:
                self.client.send_move(PlayerAction.MOVE_UP)
            elif key in ncurses_config.move_down_buttons:
                self.client.send_move(PlayerAction.MOVE_DOWN)
            elif key in ncurses_config.move_left_buttons:
                self.client.send_move(PlayerAction.MOVE_LEFT)
            elif key in ncurses_config.move_right_buttons:
                self.client.send_move(PlayerAction.MOVE_RIGHT)
            elif key in ncurses_config.drop_bomb_buttons:
                self.client.send_plant_bomb()
            elif key in ncurses_config.quit_buttons:
                self.client.is_game_running = False

            if self.client.update_semaphore.acquire(blocking=False):
                need_redraw = True


def c_main(stdscr: curses.window, args: argparse.Namespace) -> int:
    """Launches the game

    Parameters:
        stdscr: curses._CursesWindow
            The screen controller
        args: argparse.Namespace
            Parsed arguments
    """
    curses.curs_set(0)  # Do not display cursor
    handle_base_arguments(args)
    logger = logging.getLogger(f"{GAME_NAME}.ncurses")
    with CursesInterface(stdscr, logger=logger) as tui:
        tui.main_menu()

    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Instanciates a curses interface

    Parameters:
        argv: Sequence[str] | None
            If None, uses command line arguments
    """
    parser = argparse.ArgumentParser(parents=[base_parser])
    args = parser.parse_args(argv)

    return curses.wrapper(c_main, args)


if __name__ == "__main__":
    sys.exit(main())
