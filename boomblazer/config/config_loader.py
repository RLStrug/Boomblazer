"""Fuctions to load config variables from a file

Global variables:
    config_filename: pathlib.Path
        Path to the file containing the config values. Once set to a valid file
        path, it should not be modified
    config_instances: dict[str, BaseConfig]
        Mapping pointing to the dataclasse singletons

Functions:
    _find_config_file:
        Returns the usual paths where the config file should be
    load_config:
        Loads the config values from the file pointed by config_filename
    save_config:
        Saves the config values to the file pointed by config_filename
"""

import json
import logging
import pathlib
import platform
from typing import Dict
from typing import Iterator
from typing import Optional

from boomblazer.config.base_config import BaseConfig
from boomblazer.version import GAME_NAME


config_filename : Optional[pathlib.Path] = None

config_instances: Dict[str, BaseConfig] = {}

_logger = logging.getLogger(GAME_NAME)


def _find_config_file() -> Iterator[pathlib.Path]:
    """Returns the usual paths where the config file should be

    Return value: Iterator[pathlib.Path]
        The paths where the config file should be, in prefered order
    """
    os = platform.system()
    if os == "Linux":
        ...
    if os == "Darwin":
        ...
    if os == "Windows":
        ...
    # else ("Java", ""): pass
    yield pathlib.Path(".", f"{GAME_NAME}_config.json")


def load_config() -> None:
    """Loads the config values from the file pointed by config_filename
    """
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
        return

    config_values = json.load(config_filename)

    for module_name, module_values in config_values.items():
        module = config_instances.get(module_name)
        if module is None:
            continue
        module.load(module_values)


def save_config() -> None:
    """Saves the config values to the file pointed by config_filename
    """
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
