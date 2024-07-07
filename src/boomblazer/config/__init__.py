"""Configuration related modules

Submodules:
    base_config:
        Base class for configuration variables dataclasses
    client:
        Client configuration variables
    config_loader:
        Fuctions to load config variables from a file
    game:
        Game environment configuration variables
    game_folders:
        Configuration variables determining where game folders are located
    logging:
        Logging configuration variables
    server:
        Server configuration variables

Submodules not imported automatically:
        The following submodules are not automatically imported because they
        can cause errors if some conditions are not met.
        For example, .ncurses will raise an exception if the module _ncurses is
        not available
    cli:
        Command Line Interface configuration variables
    ncurses:
        Ncurses user interface configuration variables

"""

from . import base_config
from . import client
from . import config_loader
from . import game_folders
from . import logging
from . import server

__all__ = [
    "base_config",
    "client",
    "config_loader",
    "game_folders",
    "logging",
    "server",
]
