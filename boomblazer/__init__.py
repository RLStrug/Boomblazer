"""Boomblazer is a bomberman-like online multiplayer game

Submodules:
    config:
        Configuration related modules
    entity:
        Game entity modules
    game_handler:
        Handles the game state
    logging:
        Logging related modules
    map_environment:
        Implements a game map environment
    network:
        Network related modules
    ui:
        A selection of user interfaces that can be used to play the game
    version:
        Stores the software version of the game
"""

from . import config
from . import entity
from . import game_handler
from . import logging
from . import map_environment
from . import network
from . import ui
from . import version

__all__ = [
    "config",
    "entity",
    "game_handler",
    "logging",
    "map_environment",
    "network",
    "ui",
    "version",
]
