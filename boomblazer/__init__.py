"""Boomblazer is a bomberman-like online multiplayer game

Submodules:
    config:
        Configuration related modules
    environment:
        Game environment module
    logging:
        Logging related modules
    network:
        Network related modules
    ui:
        A selection of user interfaces that can be used to play the game
    version:
        Stores the software version of the game
"""

from . import config
from . import environment
from . import logging
from . import network
from . import ui
from . import version

__all__ = [
    "config",
    "environment",
    "logging",
    "network",
    "ui",
    "version",
]
