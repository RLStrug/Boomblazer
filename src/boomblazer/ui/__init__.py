"""A selection of user interfaces that can be used to play the game

Submodules:
    base_UI:
        Base UI model

Submodules not imported automatically:
        The following submodules are not automatically imported because they
        can cause errors if some conditions are not met.
        For example, .ncurses will raise an exception if the module _ncurses is
        not available
    cli:
        Implements a command line interface
    ncurses:
        Implements a curses interface
"""

from . import base_ui

__all__ = [
    "base_ui",
]
