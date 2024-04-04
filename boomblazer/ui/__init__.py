"""A selection of user interfaces that can be used to play the game

Submodules:
    base_UI:
        Base UI model
    cli:
        Implements a command line interface
    ncurses:
        Implements a curses interface
"""

from . import base_ui
from . import cli
from . import ncurses

__all__ = [
    "base_ui",
    "cli",
    "ncurses",
]
