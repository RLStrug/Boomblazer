"""Boomblazer is a bomberman-like online multiplayer game

Submodules:
    bomb:
        Implements the bombs in the game
    client:
        Implements a game client
    config:
        Game configuration variables
    fire:
        Implements the explosion fire in the game
    game_handler:
        Handles the game state
    map_environment:
        Implements a game map environment
    network:
        Implements a network communication protocol for the game
    player:
        Implements a game player
    server:
        Implements a game client
    ui:
        A selection of user interfaces that can be used to play the game
    utils:
        Defines some utility functions
    version:
        Stores the software version of the game
"""

from . import config
from . import entity
from . import game_handler
from . import map_environment
from . import network
from . import ui
from . import utils
from . import version

__all__ = [
    "config",
    "entity",
    "game_handler",
    "map_environment",
    "network",
    "ui",
    "utils",
    "version",
]
