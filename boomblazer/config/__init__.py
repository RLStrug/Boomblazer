"""Configuration related modules

Submodules:
    base_config:
        Base class for configuration variables dataclasses
    cli:
        Command Line Interface configuration variables
    client:
        Client configuration variables
    config_loader:
        Fuctions to load config variables from a file
    ncurses:
        Ncurses user interface configuration variables
    server:
        Server and game environment configuration variables
"""

from . import base_config
from . import cli
from . import client
from . import config_loader
from . import ncurses
from . import server

__all__ = [
    "base_config",
    "cli",
    "client",
    "config_loader",
    "ncurses",
    "server",
]
