"""Fuctions to load config variables from a file

Global variables:
    config_filename: pathlib.Path
        Path to the file containing the config values.
    config_instances: dict[str, BaseConfig]
        Mapping pointing to the dataclasse singletons
"""

from __future__ import annotations

import json
import logging
import pathlib
import platform
import typing

from ..metadata import GAME_NAME
from .base_config import BaseConfig
from .client import client_config
from .game import game_config
from .game_folders import game_folders_config
from .logging import logging_config
from .server import server_config

if typing.TYPE_CHECKING:
    from collections.abc import Iterator


config_filename: pathlib.Path | None = None

config_instances: dict[str, BaseConfig] = {
    "client": client_config,
    "game_folders": game_folders_config,
    "game": game_config,
    "logging": logging_config,
    "server": server_config,
}

_logger = logging.getLogger(GAME_NAME)


def _find_config_file() -> Iterator[pathlib.Path]:
    """Returns the usual paths where the config file should be

    :returns: Paths where the config file should be, in prefered order
    """
    os = platform.system()
    if os == "Linux":
        ...
    if os == "Darwin":
        ...
    if os == "Windows":
        ...
    # else ("Java", ""): pass
    yield pathlib.Path(".", f"{GAME_NAME}_data", "config", f"{GAME_NAME}_config.json")


def load_config() -> None:
    """Loads config values from the file pointed by config_filename"""
    global config_filename
    # If config file is not set, search in usual places
    if config_filename is None:
        for filename in _find_config_file():
            if filename.is_file():
                config_filename = filename
    # If a config file could not be found, keep default config values and try
    # to find a place to create a config file
    if config_filename is None:
        _logger.warning("Cannot find config file")
        save_config()
    else:
        with open(config_filename, "r", encoding="utf8") as config_file:
            config_values = json.load(config_file)

        is_config_complete = True
        for module_name, module in config_instances.items():
            module_values = config_values.get(module_name)
            if module_values is None:
                is_config_complete = False
                continue
            is_config_complete &= module.load(module_values)

        if not is_config_complete:
            save_config()

    # Create folders needed for storing extra game data
    game_folders_config.log_folder.mkdir(parents=True, exist_ok=True)
    game_folders_config.custom_maps_folder.mkdir(parents=True, exist_ok=True)


def save_config() -> None:
    """Saves config values to the file pointed by config_filename"""
    global config_filename
    # If config file is not set, search in usual places
    if config_filename is None:
        for filename in _find_config_file():
            try:
                filename.parent.mkdir(parents=True, exist_ok=True)
                filename.touch()
            except PermissionError:
                pass
            else:
                config_filename = filename
                break
    # If a config file could not be found, exit with an error message
    if config_filename is None:
        _logger.error("Cannot find a place to save the current config")
        return

    config_values = {}

    for module_name, module_values in config_instances.items():
        config_values[module_name] = module_values.dump()

    with open(config_filename, "w", encoding="utf8") as f:
        json.dump(config_values, f, indent="\t")
