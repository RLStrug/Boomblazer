"""Boomblazer is a bomberman-like online multiplayer game

Submodules:
    config:
        Configuration related modules
    entity:
        Game entity modules
    environment:
        Implements a game environment
    game_handler:
        Handles the game state
    logging:
        Logging related modules
    map:
        Implements a game map
    network:
        Network related modules
    ui:
        A selection of user interfaces that can be used to play the game
    version:
        Stores the software version of the game
"""

from . import config
from . import entity
from . import environment
from . import game_handler
from . import logging
from . import map
from . import network
from . import ui
from . import version

__all__ = [
    "config",
    "entity",
    "environment",
    "game_handler",
    "logging",
    "map",
    "network",
    "ui",
    "version",
]
