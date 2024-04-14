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
import json
import selectors
import sys
from pathlib import Path
from typing import Optional
from typing import Sequence

from boomblazer.argument_parser import base_parser
from boomblazer.config.ncurses import ncurses_config
from boomblazer.game_handler import GameHandler
from boomblazer.game_handler import MoveActionEnum
from boomblazer.map_environment import MapEnvironment
from boomblazer.ui.base_ui import BaseUI
from boomblazer.version import GAME_NAME
from boomblazer.version import VERSION_STR


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
            "HOST JOIN CREATE EXIT",
            start=0
        )
        current_choice = choices(0)
        labels = (
            "Host a game", "Join a game", "Create a game", "Exit"
        )
        while waiting:
            self.stdscr.clear()
            for idx, label in enumerate(labels):
                self.stdscr.insstr(idx, 0, label,
                    curses.A_STANDOUT if current_choice is choices(idx)
                    else curses.A_NORMAL)

            key = self.stdscr.getch()
            if key in ncurses_config.menu_down_buttons:
                current_choice += 1
            elif key in ncurses_config.menu_up_buttons:
                current_choice += len(choices) - 1
            elif key in ncurses_config.menu_select_buttons:
                waiting = False
            current_choice = choices(current_choice % len(choices))

        if current_choice is choices.HOST:
            self.join_menu(is_host=True)
        elif current_choice is choices.JOIN:
            self.join_menu(is_host=False)
        elif current_choice is choices.CREATE:
            self.create_menu()

    def join_menu(self, *, is_host: bool) -> None:
        """Gather server url and port then join

        Keyword only parameters:
            is_host: bool
                Indicates if we are the host of the game
        """
        waiting = True
        choices = enum.IntEnum(
            "JoinMenuChoiceEnum",
            "ADDRESS PORT NAME JOIN EXIT",
            start=0
        )
        current_choice = choices(0)
        labels = (
            "Server address:", "Server port:", "Player name:", "Join", "Exit",
        )
        textboxes = tuple(
            curses.textpad.Textbox(curses.newwin(
                1, curses.COLS, idx, len(labels[idx]) + 1))
            for idx in range(3)
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
            if key in ncurses_config.menu_down_buttons:
                current_choice += 1
            elif key in ncurses_config.menu_up_buttons:
                current_choice += len(choices) - 1
            elif key in ncurses_config.menu_select_buttons:
                if current_choice is choices.JOIN:
                    waiting = False
                elif current_choice is choices.EXIT:
                    return
                else:
                    curses.curs_set(1)  # Display cursor
                    textboxes[current_choice].edit()
                    curses.curs_set(0)  # Do not display cursor
                    current_choice += 1
            current_choice = choices(current_choice % len(choices))

        address = textboxes[choices.ADDRESS].gather().strip()
        port = int(textboxes[choices.PORT].gather())
        name = textboxes[choices.NAME].gather().strip()

        self.stdscr.clear()
        self.stdscr.insstr(0, 0, f"Connecting to {address}:{port}")
        self.stdscr.refresh()

        self.join_game((address, port), name, is_host=is_host)
        if self.client.is_game_running:
            self.lobby_menu()

    def create_menu(self) -> None:
        """Gather server port, game map, username, creates server, and joins it
        """
        waiting = True
        choices = enum.IntEnum(
            "JoinMenuChoiceEnum",
            "PORT MAP NAME JOIN EXIT",
            start=0
        )
        current_choice = choices(0)
        labels = (
            "Server port:", "Game map:", "Player name:", "Create", "Exit",
        )
        textboxes = tuple(
            curses.textpad.Textbox(curses.newwin(
                1, curses.COLS, idx, len(labels[idx]) + 1))
            for idx in range(3)
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
            if key in ncurses_config.menu_down_buttons:
                current_choice += 1
            elif key in ncurses_config.menu_up_buttons:
                current_choice += len(choices) - 1
            elif key in ncurses_config.menu_select_buttons:
                if current_choice is choices.JOIN:
                    waiting = False
                elif current_choice is choices.EXIT:
                    return
                else:
                    curses.curs_set(1)  # Display cursor
                    textboxes[current_choice].edit()
                    curses.curs_set(0)  # Do not display cursor
                    current_choice += 1
            current_choice = choices(current_choice % len(choices))

        port = int(textboxes[choices.PORT].gather())
        # TODO Map chooser menu
        map_filename = Path(textboxes[choices.MAP].gather().strip())
        name = textboxes[choices.NAME].gather().strip()

        self.stdscr.clear()
        self.stdscr.insstr(0, 0, f"Creating server on port {port}")
        self.stdscr.refresh()

        self.create_game_and_join(port, name, map_filename)
        if self.client.is_game_running:
            self.lobby_menu()

    def lobby_menu(self) -> None:
        """Wait in lobby for host to start game
        """
        waiting = True
        need_redraw = True
        if self.client.is_host:
            choices = enum.IntEnum(
                "LobbyMenuChoiceEnum",
                "START EXIT",
                start=0
            )
            labels = ("Start game", "Exit",)
        else:
            choices = enum.IntEnum(
                "LobbyMenuChoiceEnum",
                "EXIT",
                start=0
            )
            labels = ("Exit",)
        current_choice = choices(0)
        players_list = self.client.game_handler.map_environment.players

        self.stdscr.nodelay(True)  # User input is non blocking

        while self.client.game_handler.map_environment.version == 0:
            if need_redraw:
                need_redraw = False
                self.stdscr.clear()
                for idx, player_name in enumerate(
                        self.client.game_handler.map_environment.players
                ):
                    self.stdscr.insstr(idx, 0, player_name)
                for idx, label in enumerate(labels):
                    self.stdscr.insstr(
                        curses.LINES - len(choices) + idx, 0, label,
                        curses.A_STANDOUT if current_choice is choices(idx)
                        else curses.A_NORMAL
                    )

            key = self.stdscr.getch()
            if key != -1:
                need_redraw = True
            if key in ncurses_config.menu_down_buttons:
                current_choice += 1
            elif key in ncurses_config.menu_up_buttons:
                current_choice += len(choices) - 1
            elif key in ncurses_config.menu_select_buttons:
                if current_choice is choices.EXIT:
                    return
                self.client.send_start()
            current_choice = choices(current_choice % len(choices))

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
                self.stdscr.insstr(0, 0, str(self.client.game_handler.map_environment))

            key = self.stdscr.getch()
            if key == curses.KEY_UP or key == ord("z"):
                self.client.send_move(MoveActionEnum.MOVE_UP)
            elif key == curses.KEY_DOWN or key == ord("s"):
                self.client.send_move(MoveActionEnum.MOVE_DOWN)
            elif key == curses.KEY_LEFT or key == ord("q"):
                self.client.send_move(MoveActionEnum.MOVE_LEFT)
            elif key == curses.KEY_RIGHT or key == ord("d"):
                self.client.send_move(MoveActionEnum.MOVE_RIGHT)
            elif key == ord("\n") or key == ord("b"):
                self.client.send_plant_bomb()
            elif key == ord("Q"):
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
    verbosity = -1 if args.quiet else args.verbose
    with CursesInterface(
            stdscr, verbosity=verbosity, log_file=args.log_file
    ) as tui:
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
