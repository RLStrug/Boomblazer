"""Configuration related modules

Submodules:
    cli:
        Command Line Interface configuration variables
    client:
        Client configuration variables
    ncurses:
        Ncurses user interface configuration variables
    server:
        Server and game environment configuration variables
"""

from . import cli
from . import client
from . import ncurses
from . import server

__all__ = [
    "cli",
    "client",
    "ncurses",
    "server",
]
