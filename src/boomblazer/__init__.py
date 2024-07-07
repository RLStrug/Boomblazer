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
    utils:
        Utility module
    metadata:
        Stores the package metadata
"""

from . import config
from . import environment
from . import logging
from . import metadata
from . import network
from . import ui
from . import utils

__all__ = [
    "config",
    "environment",
    "logging",
    "network",
    "ui",
    "utils",
    "metadata",
]
